# PHAN TICH NGHIEP VU HE THONG

## 1. Muc tieu he thong
He thong duoc xay dung tren Odoo 15 (Python) de quan ly dong bo 3 nghiep vu chinh:
- Quan ly nhan su noi bo (ho so nhan vien, cham cong, bang luong).
- Quan ly khach hang va ho tro khach hang.
- Quan ly cong viec, tu dong tao va phan cong cong viec tu ticket ho tro.

Muc tieu toi uu:
- Giam thao tac thu cong khi xu ly ticket.
- Tang toc do phan cong cong viec.
- Dam bao nguoi xu ly phu hop theo vung mien va tai trong cong viec.
- Minh bach hoa thong tin va thong ke quan tri.

## 2. Pham vi module
- Module 1: `nhan_su`
- Module 2: `quan_ly_khach_hang`
- Module 3: `quan_ly_cong_viec`

`quan_ly_khach_hang` va `quan_ly_cong_viec` deu phu thuoc truc tiep vao `nhan_su`, dam bao dat yeu cau ket hop bat buoc voi module Quan ly nhan su.

## 3. Phan tich nghiep vu tung module

### 3.1. Module nhan_su

#### 3.1.1. Doi tuong du lieu chinh
- Nhan vien (`nhan.vien`): ho ten, ma dinh danh, user lien ket, vung mien, luong co ban, phu cap.
- Cham cong (`cham.cong`): gio vao, gio ra, so gio lam, gio thieu, OT, vi pham di muon/ve som, tien phat, tien OT.
- Bang luong (`bang.luong`): tong hop cong, phat, OT, phu cap, thuong, tong luong, trang thai chi tra.

#### 3.1.2. Quy tac nghiep vu
- Cham cong tu dong tinh:
  - So gio lam dua tren `gio_ra - gio_vao`.
  - Gio thieu theo chuan 8 gio/ngay.
  - Di muon neu vao sau 08:00; ve som neu ra truoc 17:00.
  - Tien phat: di muon + ve som + thieu gio.
  - Tien OT: gio OT * don gia OT.
- Bang luong tu dong tong hop theo thang/nam:
  - Lay du lieu cham cong da hoan thanh trong ky luong.
  - Tinh luong ngay = luong co ban / so ngay cong chuan.
  - Tong luong = luong theo cong + phu cap + thuong - tong phat + tong OT.
- Luong co quy trinh trang thai: nhap -> xac_nhan -> da_tra.

#### 3.1.3. Gia tri quan tri
- Chuan hoa quy trinh cham cong - tinh luong.
- Giam sai sot khi tinh thu cong.
- Co co so du lieu de ket hop phan cong cong viec theo nang luc/tai trong.

### 3.2. Module quan_ly_khach_hang

#### 3.2.1. Doi tuong du lieu chinh
- Khach hang (`thong_tin_khach_hang`): thong tin co ban, vung mien, nhan vien phu trach.
- Don hang (`chi_tiet_don_hang`): san pham, so luong, thanh tien, trang thai.
- Ho tro khach hang (`ho_tro_khach_hang`): muc uu tien, mo ta, thoi gian xu ly, nhan vien phu trach, danh gia.
- Thong ke ho tro nhan vien (`thong_ke_ho_tro_nhan_vien`).
- Phan tich khach hang theo mien (`phan_tich_khach_hang_theo_mien`).

#### 3.2.2. Quy tac nghiep vu
- Khach hang bat buoc co vung mien de phuc vu phan tich va phan cong theo khu vuc.
- Don hang tu dong tinh thanh tien theo so luong * don gia.
- Ho tro khach hang:
  - Co muc uu tien (thap/trung_binh/cao/khan_cap).
  - Rang buoc du lieu diem danh gia va dieu kien nhap ket qua ho tro.
- Tu dong cap nhat thong ke:
  - Theo nhan vien phu trach ticket.
  - Theo khu vuc khach hang (bac/trung/nam).

#### 3.2.3. Gia tri quan tri
- Nhanh chong nam bat tinh hinh khach hang.
- Theo doi chat luong ho tro qua diem danh gia.
- Ho tro ra quyet dinh qua dashboard/phan tich khu vuc.

### 3.3. Module quan_ly_cong_viec

#### 3.3.1. Doi tuong du lieu chinh
- Cong viec (`task`): ten, mo ta, deadline, priority, state, leader, members.
- Cong viec cua toi (`my_task`): view ca nhan theo user va vai tro.
- Mo rong nhan vien (`nhan_vien_extend`): so cong viec dang ganh, so khach hang phu trach.
- Dich vu AI (`gemini.ai.service`): de xuat nhan vien phan cong.

#### 3.3.2. Quy tac nghiep vu
- Khi tao task ma chua co `leader_id`, he thong goi AI de de xuat nhan vien phu hop.
- Co co che fallback neu AI loi/qua han muc: chon nguoi it viec nhat.
- Co rang buoc cung o tang code:
  - Neu task khong khan cap va khach co vung mien, uu tien nguoi cung vung.
- Tu dong dong bo task sang danh sach `my_task` theo user de theo doi ca nhan.

#### 3.3.3. Gia tri quan tri
- Rut ngan thoi gian phan cong.
- Can bang tai trong nhan vien.
- Tang kha nang dap ung ticket dung nguoi, dung khu vuc.

## 4. Phan tich nghiep vu ket hop giua cac module

### 4.1. Ket hop nhan_su <-> quan_ly_khach_hang
- Khach hang co truong `nhan_vien_phu_trach_id` lien ket sang `nhan.vien`.
- He thong thong ke so lan ho tro theo nhan vien de danh gia nang suat.
- Du lieu vung mien nhan vien duoc su dung de ket hop voi vung mien khach hang.

### 4.2. Ket hop nhan_su <-> quan_ly_cong_viec
- Task dung model `nhan.vien` cho `leader_id` va `member_ids`.
- Module cong viec mo rong nhan vien de tinh `task_count` phuc vu dieu pho.
- Du lieu luong co ban va vung mien cua nhan vien la dau vao cho AI ranking.

### 4.3. Ket hop quan_ly_khach_hang <-> quan_ly_cong_viec
- Khi tao ticket ho tro moi, he thong tu dong tao task tuong ung.
- Mapping muc uu tien ticket sang priority task.
- Task luu lien ket nguoc ve ticket va khach hang de truy vet.

### 4.4. Chuoi nghiep vu lien thong dau-cuoi
1. Nhan vien CSKH tiep nhan ticket.
2. He thong tao task tu dong voi deadline theo muc uu tien.
3. AI de xuat nguoi phu trach dua tren:
   - Muc do khan cap.
   - Vung mien khach hang.
   - Tai trong hien tai cua nhan vien.
4. Neu AI that bai, fallback chon nguoi it viec nhat.
5. Nhan vien cap nhat tien do task tren my_task/task.
6. Quan ly theo doi KPI qua thong ke ho tro va bao cao khu vuc.

## 5. Dinh nghia vai tro nghiep vu
- Nhan vien nhan su: quan ly ho so, cham cong, bang luong.
- Nhan vien CSKH: tiep nhan va nhap ticket ho tro.
- Truong nhom/nhan vien xu ly: nhan task, cap nhat tien do, hoan thanh.
- Quan ly: theo doi dashboard, thong ke, nang suat nhan vien.
- He thong AI: ho tro quyet dinh phan cong ban dau.

## 6. Quy tac va rang buoc quan trong
- Ticket phai co khach hang.
- Khach hang phai co vung mien.
- Task tao tu ticket duoc uu tien phan cong theo cung vung (tru task khan cap).
- Khong de trong nguoi phu trach task khi quy trinh auto assignment dang bat.
- Neu AI khong san sang, he thong van phai tao va gan task qua fallback.

## 7. Chi so danh gia hieu qua de tai
- Thoi gian trung binh tu luc tao ticket den luc co nguoi phu trach task.
- Ty le task duoc gan dung vung mien.
- So luong ticket xu ly/nhan vien theo ky.
- Ty le task qua han.
- Diem danh gia ho tro trung binh theo nhan vien.

## 8. Ket luan nghiep vu
He thong da co kien truc nghiep vu lien thong giua nhan su - khach hang - cong viec va co thanh phan AI ho tro phan cong tu dong. Day la nen tang phu hop de trien khai san pham Odoo 15 trong boi canh quan ly ho tro khach hang va van hanh nhan su noi bo.
