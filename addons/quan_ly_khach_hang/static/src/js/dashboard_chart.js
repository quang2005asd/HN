odoo.define('dashboard_chart', function(require) {
    "use strict";

    var rpc = require('web.rpc');

    var chartInstances = {};
    var isLoading = false;
    var lastRenderTs = 0;

    function formatMoney(value) {
        return (value || 0).toLocaleString('vi-VN') + ' ₫';
    }

    function animateCounter(element, finalValue, formatter) {
        if (!element) {
            return;
        }
        var start = 0;
        var end = Number(finalValue) || 0;
        var frame = 0;
        var totalFrames = 24;
        var step = function () {
            frame += 1;
            var progress = frame / totalFrames;
            var eased = 1 - Math.pow(1 - progress, 3);
            var current = Math.round(start + ((end - start) * eased));
            element.textContent = formatter ? formatter(current) : String(current);
            if (frame < totalFrames) {
                requestAnimationFrame(step);
            }
        };
        requestAnimationFrame(step);
    }

    function updateKpis(customerData, spendingData) {
        var totalCustomers = customerData.reduce(function (acc, val) { return acc + (val || 0); }, 0);
        var totalSpending = spendingData.reduce(function (acc, val) { return acc + (val || 0); }, 0);
        var avgSpending = totalCustomers ? (totalSpending / totalCustomers) : 0;

        var regions = ["Miền Bắc", "Miền Trung", "Miền Nam"];
        var maxIndex = 0;
        customerData.forEach(function (value, index) {
            if (value > customerData[maxIndex]) {
                maxIndex = index;
            }
        });

        animateCounter(document.getElementById('kpiTotalCustomers'), totalCustomers);
        animateCounter(document.getElementById('kpiTotalSpending'), totalSpending, formatMoney);
        animateCounter(document.getElementById('kpiAvgSpending'), avgSpending, formatMoney);

        var topRegionEl = document.getElementById('kpiTopRegion');
        if (topRegionEl) {
            topRegionEl.textContent = regions[maxIndex];
        }
    }

    function loadCharts() {
            if (isLoading) {
                return;
            }
            isLoading = true;
            rpc.query({
                model: 'dashboard',
                method: 'search_read',
                fields: ['so_luong_khach_bac', 'so_luong_khach_trung', 'so_luong_khach_nam',
                         'tong_chi_tieu_bac', 'tong_chi_tieu_trung', 'tong_chi_tieu_nam']
            }).then(function (data) {
                if (data.length === 0) {
                    return;
                }

                var dashboardData = data[0];

                var customerData = [
                    dashboardData.so_luong_khach_bac,
                    dashboardData.so_luong_khach_trung,
                    dashboardData.so_luong_khach_nam
                ];

                var spendingData = [
                    dashboardData.tong_chi_tieu_bac,
                    dashboardData.tong_chi_tieu_trung,
                    dashboardData.tong_chi_tieu_nam
                ];

                var labels = ["Miền Bắc", "Miền Trung", "Miền Nam"];
                updateKpis(customerData, spendingData);

                renderChart("customerChart", "doughnut", "Tổng số khách hàng", labels, customerData, ['#2f84d6', '#6fa9f0', '#9dd0ff']);
                renderChart("spendingChart", "bar", "Tổng chi tiêu", labels, spendingData, ['#12a594', '#36b6a7', '#6fd7ca']);
                lastRenderTs = Date.now();
            }).catch(function (error) {
                console.error("Lỗi khi gọi RPC:", error);
            }).finally(function () {
                isLoading = false;
            });
        }

        function renderChart(canvasId, type, title, labels, data, colors) {
            var canvas = document.getElementById(canvasId);
            if (!canvas) {
                return;
            }

            if (chartInstances[canvasId]) {
                chartInstances[canvasId].destroy();
            }

            var ctx = canvas.getContext('2d');

            chartInstances[canvasId] = new Chart(ctx, {
                type: type,
                data: {
                    labels: labels,
                    datasets: [{
                        label: title,
                        data: data,
                        backgroundColor: colors,
                        borderColor: colors,
                        borderWidth: type === 'bar' ? 0 : 2,
                        hoverOffset: 8,
                        borderRadius: type === 'bar' ? 10 : 0,
                        maxBarThickness: 56
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: type === 'doughnut' ? '58%' : undefined,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 16,
                                boxWidth: 12,
                                usePointStyle: true
                            }
                        }
                    },
                    scales: type === 'bar' ? {
                        y: { beginAtZero: true, grid: { color: 'rgba(20,60,96,0.08)' } },
                        x: { grid: { display: false } }
                    } : undefined
                }
            });
        }

    function bootDashboardCharts() {
        var canvas = document.getElementById('customerChart');
        if (!canvas) {
            return;
        }

        // Tránh gọi RPC dồn dập khi DOM thay đổi liên tục
        if (Date.now() - lastRenderTs < 1200) {
            return;
        }
        loadCharts();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            setTimeout(bootDashboardCharts, 200);
        });
    } else {
        setTimeout(bootDashboardCharts, 200);
    }

    // Odoo backend là SPA, cần canh dashboard xuất hiện sau khi chuyển menu/action
    setInterval(bootDashboardCharts, 900);
});
