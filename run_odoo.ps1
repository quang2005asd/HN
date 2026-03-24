param(
    [switch]$Upgrade,
    [string]$Modules = "quan_ly_cong_viec,quan_ly_khach_hang"
)

$Root = "C:/Users/quang/odoo-fitdnu"
$Py = "/mnt/c/Users/quang/odoo-fitdnu/venv/bin/python3"
$Odoo = "/mnt/c/Users/quang/odoo-fitdnu/odoo-bin.py"
$Conf = "/mnt/c/Users/quang/odoo-fitdnu/odoo.conf"
$Db = "odoo_fitdnu_clean"
$Log = "/mnt/c/Users/quang/odoo-fitdnu/odoo_run.log"

wsl bash -c "pkill -f odoo-bin.py 2>/dev/null"

if ($Upgrade) {
    wsl bash -c "$Py $Odoo -c $Conf -d $Db -u $Modules --stop-after-init > $Log 2>&1"
}

wsl bash -c "nohup $Py $Odoo -c $Conf -d $Db > $Log 2>&1 &"
Start-Sleep -Seconds 12
wsl bash -c "grep -E 'HTTP service|Modules loaded|ERROR|CRITICAL' $Log | tail -10"

