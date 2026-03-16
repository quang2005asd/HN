# -*- coding: utf-8 -*-
import json
import logging
import time
import requests

_logger = logging.getLogger(__name__)

GEMINI_API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

from odoo import models, api


class GeminiAIService(models.AbstractModel):
    _name = 'gemini.ai.service'
    _description = 'Dịch vụ AI Gemini - Tự động phân công công việc'

    def _get_api_key(self):
        return self.env['ir.config_parameter'].sudo().get_param('gemini.api_key', '')

    def _get_model_name(self):
        return self.env['ir.config_parameter'].sudo().get_param('gemini.model', 'gemini-2.0-flash')

    def _fallback_nhan_vien_it_viec_nhat(self, nhan_vien_list, ly_do):
        best = min(nhan_vien_list, key=lambda x: x['task_count'])
        _logger.warning("Fallback phân công NV ID=%s - %s", best['id'], ly_do)
        return best['id'], ly_do

    def phan_cong_nhan_vien(self, task_info, nhan_vien_list):
        """
        Gửi thông tin task + danh sách nhân viên lên Gemini.
        Trả về: (nhan_vien_id, ly_do) hoặc (None, thông báo lỗi)
        """
        if not nhan_vien_list:
            return None, "Không có nhân viên nào trong hệ thống"

        api_key = self._get_api_key()
        if not api_key:
            return self._fallback_nhan_vien_it_viec_nhat(
                nhan_vien_list,
                "Chưa cấu hình Gemini API key, tự động chọn người ít việc nhất"
            )

        try:
            prompt = self._build_prompt(task_info, nhan_vien_list)
            model_name = self._get_model_name()
            api_url = GEMINI_API_URL_TEMPLATE.format(model=model_name)
            _logger.info("Gửi request Gemini (%s) phân công task: %s", model_name, task_info.get('name'))

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 256},
            }
            resp = None
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                resp = requests.post(
                    api_url,
                    params={"key": api_key},
                    json=payload,
                    timeout=15,
                )

                # Thành công hoặc lỗi không nên retry
                if resp.status_code < 400 or resp.status_code not in (429, 500, 502, 503, 504):
                    break

                if attempt < max_attempts:
                    wait_seconds = attempt
                    _logger.warning(
                        "Gemini trả về %s (attempt %s/%s), retry sau %ss",
                        resp.status_code,
                        attempt,
                        max_attempts,
                        wait_seconds,
                    )
                    time.sleep(wait_seconds)

            resp.raise_for_status()
            response_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            nhan_vien_id, ly_do = self._parse_response(response_text, nhan_vien_list)

            _logger.info("Gemini chọn NV ID=%s, lý do: %s", nhan_vien_id, ly_do)
            return nhan_vien_id, ly_do

        except Exception as e:
            _logger.error("Lỗi Gemini API: %s", str(e))
            return self._fallback_nhan_vien_it_viec_nhat(
                nhan_vien_list,
                f"Gemini lỗi API, tự động chọn người ít việc nhất: {str(e)}"
            )

    def _build_prompt(self, task_info, nhan_vien_list):
        priority_map = {
            '0': 'Thấp',
            '1': 'Bình thường',
            '2': 'Cao',
            '3': 'Khẩn cấp',
        }
        vung_mien_map = {
            'bac': 'Miền Bắc',
            'trung': 'Miền Trung',
            'nam': 'Miền Nam',
            '': 'Chưa xác định',
        }

        nv_lines = []
        for i, nv in enumerate(nhan_vien_list):
            vung = vung_mien_map.get(nv.get('vung_mien', ''), 'Chưa xác định')
            nv_lines.append(
                f"{i + 1}. [ID:{nv['id']}] {nv['name']} "
                f"| Khu vực: {vung} "
                f"| Task hiện tại: {nv['task_count']} "
                f"| Lương: {nv['luong_co_ban']:,.0f} VNĐ"
            )

        priority_label = priority_map.get(str(task_info.get('priority', '1')), 'Bình thường')
        vung_kh = vung_mien_map.get(task_info.get('vung_mien_kh', ''), 'Chưa xác định')

        return f"""Bạn là hệ thống phân công công việc thông minh cho doanh nghiệp Việt Nam.

CÔNG VIỆC CẦN PHÂN CÔNG:
- Tên: {task_info['name']}
- Mô tả: {task_info.get('description') or 'Không có'}
- Mức ưu tiên: {priority_label}
- Khách hàng: {task_info.get('khach_hang') or 'Không có'}
- Khu vực khách hàng: {vung_kh}
- Hạn chót: {task_info.get('deadline') or 'Không có'}

DANH SÁCH NHÂN VIÊN:
{chr(10).join(nv_lines)}

QUY TẮC PHÂN CÔNG (theo thứ tự ưu tiên):
1. Ưu tiên nhân viên cùng khu vực với khách hàng
2. Ưu tiên nhân viên có ít task nhất (workload thấp)
3. Task khẩn cấp → chọn người ít việc nhất, bất kể khu vực
4. Nhân viên lương cao hơn = kinh nghiệm nhiều hơn

Trả lời CHÍNH XÁC theo định dạng JSON sau, KHÔNG thêm bất kỳ text nào khác:
{{"nhan_vien_id": <số ID>, "ten": "<tên nhân viên>", "ly_do": "<lý do ngắn gọn 1 câu bằng tiếng Việt>"}}"""

    def _parse_response(self, response_text, nhan_vien_list):
        try:
            text = response_text.strip()

            # Xử lý nếu Gemini trả về markdown code block
            if '```' in text:
                for part in text.split('```'):
                    if '{' in part:
                        text = part.strip()
                        if text.startswith('json'):
                            text = text[4:].strip()
                        break

            data = json.loads(text)
            nhan_vien_id = int(data.get('nhan_vien_id', 0))
            ly_do = data.get('ly_do', 'Được Gemini AI lựa chọn')

            # Kiểm tra ID có hợp lệ không
            valid_ids = [nv['id'] for nv in nhan_vien_list]
            if nhan_vien_id in valid_ids:
                return nhan_vien_id, ly_do

            _logger.warning("Gemini trả về ID %s không hợp lệ, fallback chọn người ít task nhất", nhan_vien_id)

        except Exception as e:
            _logger.error("Lỗi parse Gemini response: %s\nResponse gốc: %s", str(e), response_text)

        # Fallback: chọn người ít task nhất
        return self._fallback_nhan_vien_it_viec_nhat(
            nhan_vien_list,
            "Gemini trả về dữ liệu không hợp lệ, tự động chọn người ít việc nhất"
        )
