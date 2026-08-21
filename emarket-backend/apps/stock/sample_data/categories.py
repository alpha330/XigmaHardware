"""Product taxonomy for the stock sample catalog.

Brands and product condition deliberately stay out of this tree because both are
already first-class fields on :class:`stock.Product`.
"""


def leaf(name, slug):
    return {"name": name, "slug": slug, "category_type": "series"}


def group(name, slug, *children):
    return {
        "name": name,
        "slug": slug,
        "category_type": "type",
        "children": children,
    }


def root(name, slug, *children):
    return {
        "name": name,
        "slug": slug,
        "category_type": "usage",
        "is_featured": True,
        "children": children,
    }


CATEGORY_TREE = (
    root(
        "دیتاسنتر و مراکز داده",
        "data-center",
        group(
            "پردازش و سرور",
            "dc-compute",
            leaf("سرور رک‌مونت", "dc-rack-server"),
            leaf("سرور ایستاده", "dc-tower-server"),
            leaf("سرور تیغه‌ای و ماژولار", "dc-blade-server"),
            leaf("سرور لبه شبکه", "dc-edge-server"),
            leaf("سرور هوش مصنوعی و GPU", "dc-ai-gpu-server"),
        ),
        group(
            "قطعات سرور",
            "dc-server-components",
            leaf("پردازنده سرور", "dc-server-cpu"),
            leaf("مادربرد سرور", "dc-server-motherboard"),
            leaf("حافظه ECC و RDIMM", "dc-server-memory"),
            leaf("کارت RAID و HBA", "dc-raid-hba"),
            leaf("شتاب‌دهنده و GPU دیتاسنتر", "dc-accelerator"),
            leaf("شاسی سرور", "dc-server-chassis"),
            leaf("پاور سرور", "dc-server-psu"),
        ),
        group(
            "ذخیره‌سازی سازمانی",
            "dc-enterprise-storage",
            leaf("ذخیره‌ساز SAN", "dc-san-array"),
            leaf("ذخیره‌ساز NAS سازمانی", "dc-enterprise-nas"),
            leaf("ذخیره‌ساز DAS و JBOD", "dc-das-jbod"),
            leaf("کتابخانه نوار و بکاپ", "dc-tape-library"),
            leaf("هارددیسک Enterprise", "dc-enterprise-hdd"),
            leaf("SSD سازمانی SATA و SAS", "dc-enterprise-sata-sas-ssd"),
            leaf("SSD سازمانی NVMe", "dc-enterprise-nvme"),
        ),
        group(
            "شبکه دیتاسنتر",
            "dc-network",
            leaf("سوییچ Core و دیتاسنتر", "dc-core-switch"),
            leaf("روتر سازمانی", "dc-enterprise-router"),
            leaf("فایروال و UTM", "dc-firewall-utm"),
            leaf("لود بالانسر", "dc-load-balancer"),
            leaf("کارت شبکه سرور", "dc-server-nic"),
            leaf("ماژول و ترنسیور شبکه", "dc-transceiver"),
            leaf("کابل مسی و فیبر نوری", "dc-cabling"),
        ),
        group(
            "زیرساخت فیزیکی",
            "dc-infrastructure",
            leaf("رک و متعلقات", "dc-rack-accessories"),
            leaf("UPS دیتاسنتر", "dc-ups"),
            leaf("PDU و توزیع برق", "dc-pdu"),
            leaf("KVM و کنسول", "dc-kvm-console"),
            leaf("سرمایش دیتاسنتر", "dc-cooling"),
        ),
    ),
    root(
        "سازمانی و اداری",
        "office-enterprise",
        group(
            "رایانه سازمانی",
            "office-computers",
            leaf("کامپیوتر رومیزی اداری", "office-desktop"),
            leaf("مینی پی‌سی اداری", "office-mini-pc"),
            leaf("کامپیوتر All-in-One", "office-all-in-one"),
            leaf("تین کلاینت و زیرو کلاینت", "office-thin-client"),
        ),
        group(
            "لپ‌تاپ سازمانی",
            "office-laptops",
            leaf("لپ‌تاپ تجاری", "office-business-laptop"),
            leaf("اولترابوک سازمانی", "office-ultrabook"),
            leaf("لپ‌تاپ دوکاره", "office-convertible-laptop"),
        ),
        group(
            "شبکه اداری",
            "office-network",
            leaf("سوییچ Access", "office-access-switch"),
            leaf("روتر شعب و دفاتر", "office-branch-router"),
            leaf("فایروال اداری", "office-firewall"),
            leaf("اکسس پوینت و کنترلر", "office-access-point"),
            leaf("کارت و مبدل شبکه", "office-network-adapter"),
        ),
        group(
            "تجهیزات جانبی اداری",
            "office-peripherals",
            leaf("مانیتور اداری", "office-monitor"),
            leaf("پرینتر و دستگاه چندکاره", "office-printer-mfp"),
            leaf("اسکنر", "office-scanner"),
            leaf("کیبورد و ماوس اداری", "office-keyboard-mouse"),
            leaf("وب‌کم و هدست کنفرانس", "office-conference"),
            leaf("داک و هاب", "office-dock-hub"),
        ),
        group(
            "ذخیره‌سازی و برق اداری",
            "office-storage-power",
            leaf("NAS اداری", "office-nas"),
            leaf("ذخیره‌ساز اکسترنال اداری", "office-external-storage"),
            leaf("UPS اداری", "office-ups"),
        ),
    ),
    root(
        "خانگی و شخصی",
        "home",
        group(
            "کامپیوتر و لپ‌تاپ خانگی",
            "home-computers",
            leaf("کامپیوتر اسمبل‌شده", "home-custom-pc"),
            leaf("کامپیوتر گیمینگ آماده", "home-gaming-desktop"),
            leaf("مینی پی‌سی خانگی", "home-mini-pc"),
            leaf("لپ‌تاپ روزمره", "home-everyday-laptop"),
            leaf("لپ‌تاپ گیمینگ", "home-gaming-laptop"),
            leaf("لپ‌تاپ تولید محتوا", "home-creator-laptop"),
        ),
        group(
            "قطعات کامپیوتر",
            "home-pc-components",
            leaf("پردازنده دسکتاپ", "home-desktop-cpu"),
            leaf("مادربرد دسکتاپ", "home-motherboard"),
            leaf("حافظه RAM دسکتاپ", "home-desktop-memory"),
            leaf("کارت گرافیک گیمینگ", "home-gaming-gpu"),
            leaf("هارددیسک داخلی", "home-internal-hdd"),
            leaf("SSD ساتا", "home-sata-ssd"),
            leaf("SSD نوع M.2 NVMe", "home-nvme-m2"),
            leaf("کیس کامپیوتر", "home-pc-case"),
            leaf("پاور کامپیوتر", "home-pc-psu"),
            leaf("خنک‌کننده بادی", "home-air-cooling"),
            leaf("خنک‌کننده مایع", "home-liquid-cooling"),
            leaf("کارت صدا و کپچر", "home-sound-capture"),
        ),
        group(
            "شبکه خانگی",
            "home-network",
            leaf("مودم و مودم‌روتر", "home-modem-router"),
            leaf("روتر Wi-Fi", "home-wifi-router"),
            leaf("سیستم Wi-Fi مش", "home-mesh-wifi"),
            leaf("اکسس پوینت خانگی", "home-access-point"),
            leaf("کارت شبکه و دانگل", "home-network-adapter"),
        ),
        group(
            "لوازم جانبی شخصی",
            "home-peripherals",
            leaf("مانیتور گیمینگ", "home-gaming-monitor"),
            leaf("مانیتور عمومی", "home-general-monitor"),
            leaf("کیبورد", "home-keyboard"),
            leaf("ماوس", "home-mouse"),
            leaf("هدست و اسپیکر", "home-audio"),
            leaf("وب‌کم و تجهیزات استریم", "home-streaming"),
        ),
        group(
            "ذخیره‌سازی شخصی",
            "home-personal-storage",
            leaf("NAS خانگی", "home-nas"),
            leaf("هارد اکسترنال", "home-external-hdd"),
            leaf("SSD اکسترنال", "home-external-ssd"),
            leaf("فلش و کارت حافظه", "home-flash-memory"),
        ),
    ),
    root(
        "ورک‌استیشن حرفه‌ای",
        "workstation",
        group(
            "سیستم ورک‌استیشن",
            "workstation-systems",
            leaf("ورک‌استیشن رومیزی", "workstation-desktop"),
            leaf("ورک‌استیشن همراه", "workstation-mobile"),
            leaf("ورک‌استیشن هوش مصنوعی", "workstation-ai"),
        ),
        group(
            "قطعات ورک‌استیشن",
            "workstation-components",
            leaf("پردازنده ورک‌استیشن", "workstation-cpu"),
            leaf("کارت گرافیک حرفه‌ای", "workstation-professional-gpu"),
            leaf("حافظه ECC ورک‌استیشن", "workstation-ecc-memory"),
            leaf("مادربرد ورک‌استیشن", "workstation-motherboard"),
            leaf("ذخیره‌ساز NVMe حرفه‌ای", "workstation-nvme"),
        ),
        group(
            "تجهیزات حرفه‌ای",
            "workstation-peripherals",
            leaf("مانیتور حرفه‌ای", "workstation-monitor"),
            leaf("داک ورک‌استیشن", "workstation-dock"),
            leaf("تجهیزات ورودی حرفه‌ای", "workstation-input"),
        ),
    ),
)
