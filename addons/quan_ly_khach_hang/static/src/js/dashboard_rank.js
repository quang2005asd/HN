odoo.define('dashboard_rank', function(require) {
    "use strict";

    var rpc = require('web.rpc');
    var rankingChartInstance;
    var isLoading = false;
    var lastRenderTs = 0;

    function formatMoney(value) {
        return (value || 0).toLocaleString('vi-VN') + ' ₫';
    }

    function loadRanking() {
            if (isLoading) {
                return;
            }
            isLoading = true;
            rpc.query({
                model: 'bang_xep_hang_khach_hang',  // Lấy từ model xếp hạng
                method: 'search_read',
                fields: ['khach_hang_id', 'tong_tien_chi_tieu', 'xep_hang']
            }).then(function (data) {
                if (data.length === 0) {
                    return;
                }

                renderTable(data);
                renderChart(data);
                updateTopCustomer(data);
                lastRenderTs = Date.now();
            }).catch(function (error) {
                console.error("Lỗi khi gọi RPC:", error);
            }).finally(function () {
                isLoading = false;
            });
        }

        function updateTopCustomer(data) {
            var el = document.getElementById('kpiTopCustomer');
            if (!el || !data.length || !data[0].khach_hang_id) {
                return;
            }
            el.textContent = data[0].khach_hang_id[1];
        }

        function renderTable(data) {
            var tableBody = $("#rankingTable tbody");
            tableBody.empty();

            data.forEach(function (item, index) {
                var row = `<tr>
                    <td>${item.xep_hang}</td>
                    <td>${item.khach_hang_id[1]}</td>
                    <td>${formatMoney(item.tong_tien_chi_tieu)}</td>
                </tr>`;
                tableBody.append(row);
            });
        }

        function renderChart(data) {
            var canvas = document.getElementById("rankingChart");
            if (!canvas) {
                return;
            }

            var ctx = canvas.getContext('2d');
            if (rankingChartInstance) {
                rankingChartInstance.destroy();
            }

            // Chuẩn bị dữ liệu
            var labels = data.map(item => item.khach_hang_id[1]);  // Tên khách hàng
            var totalSpending = data.map(item => item.tong_tien_chi_tieu);  // Tổng chi tiêu

            rankingChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Tổng tiền chi tiêu",
                        data: totalSpending,
                        backgroundColor: ['#1f6cb2', '#2d88d8', '#57a0e6', '#84b8f0', '#add0f8'],
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

    function bootRanking() {
        var chart = document.getElementById('rankingChart');
        var table = document.getElementById('rankingTable');
        if (!chart || !table) {
            return;
        }
        if (Date.now() - lastRenderTs < 1200) {
            return;
        }
        loadRanking();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            setTimeout(bootRanking, 240);
        });
    } else {
        setTimeout(bootRanking, 240);
    }

    setInterval(bootRanking, 1000);
});
