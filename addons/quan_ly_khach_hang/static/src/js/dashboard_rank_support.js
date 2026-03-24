odoo.define('thong_ke_ho_tro', function(require) {
    "use strict";

    var rpc = require('web.rpc');
    var supportChartInstance;
    var isLoading = false;
    var lastRenderTs = 0;

    function loadSupportStats() {
            if (isLoading) {
                return;
            }
            isLoading = true;
            rpc.query({
                model: 'thong_ke_ho_tro_nhan_vien',
                method: 'search_read',
                fields: ['nhan_vien_id', 'so_lan_ho_tro']
            }).then(function (data) {
                if (data.length === 0) {
                    return;
                }

                renderTable(data);
                renderChart(data);
                updateTopSupport(data);
                lastRenderTs = Date.now();
            }).catch(function (error) {
                console.error("Lỗi khi gọi RPC:", error);
            }).finally(function () {
                isLoading = false;
            });
        }

        function updateTopSupport(data) {
            var el = document.getElementById('kpiTopSupport');
            if (!el || !data.length || !data[0].nhan_vien_id) {
                return;
            }
            el.textContent = data[0].nhan_vien_id[1];
        }

        function renderTable(data) {
            var tableBody = $("#supportStatsTable tbody");
            tableBody.empty();

            data.forEach(function (item) {
                var row = `<tr>
                    <td>${item.nhan_vien_id[1]}</td>
                    <td>${item.so_lan_ho_tro}</td>
                </tr>`;
                tableBody.append(row);
            });
        }

        function renderChart(data) {
            var canvas = document.getElementById("supportChart");
            if (!canvas) {
                return;
            }

            var ctx = canvas.getContext('2d');
            if (supportChartInstance) {
                supportChartInstance.destroy();
            }

            var labels = data.map(item => item.nhan_vien_id[1]);  // Tên nhân viên
            var supportCounts = data.map(item => item.so_lan_ho_tro);  // Số lần hỗ trợ
            var gradient = ctx.createLinearGradient(0, 0, 0, 320);
            gradient.addColorStop(0, 'rgba(18, 165, 148, 0.88)');
            gradient.addColorStop(1, 'rgba(18, 165, 148, 0.42)');

            supportChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Số lần hỗ trợ",
                        data: supportCounts,
                        backgroundColor: gradient,
                        borderColor: 'rgba(18, 165, 148, 1)',
                        borderWidth: 0,
                        borderRadius: 10,
                        borderSkipped: false,
                        maxBarThickness: 48
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(22, 66, 108, 0.08)' }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
        }

    function bootSupportStats() {
        var chart = document.getElementById('supportChart');
        var table = document.getElementById('supportStatsTable');
        if (!chart || !table) {
            return;
        }
        if (Date.now() - lastRenderTs < 1200) {
            return;
        }
        loadSupportStats();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            setTimeout(bootSupportStats, 280);
        });
    } else {
        setTimeout(bootSupportStats, 280);
    }

    setInterval(bootSupportStats, 1000);
});
