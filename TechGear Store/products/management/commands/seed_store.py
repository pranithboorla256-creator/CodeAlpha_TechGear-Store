from django.core.management.base import BaseCommand
from django.conf import settings
import json
from django.utils.text import slugify
from products.models import Category, Product

DATA = {
 "Laptops": [("Lenovo IdeaPad Slim 5","Lenovo",64990,59990),("HP Pavilion 15","HP",58990,None),("ASUS VivoBook 15","ASUS",54990,49990),("Dell Inspiron 15","Dell",62990,None),("Acer Aspire 5","Acer",47990,44990)],
 "Keyboards": [("Logitech K380","Logitech",3495,2995),("Logitech MX Keys S","Logitech",12995,None),("Redragon K552","Redragon",4999,4299),("HP Mechanical Gaming Keyboard","HP",5999,None),("Keychron K2 Wireless","Keychron",8999,7999)],
 "Mice": [("Logitech M331 Silent","Logitech",1595,None),("Logitech MX Master 3S","Logitech",10995,9995),("Razer DeathAdder Essential","Razer",2499,1999),("HP 280 Wireless Mouse","HP",1299,None),("Redragon M808 Storm","Redragon",2999,2499)],
 "Headphones": [("Sony WH-CH520","Sony",4490,3990),("JBL Tune 760NC","JBL",7999,6999),("boAt Rockerz 450","boAt",1999,None),("HyperX Cloud II","HyperX",8999,7999),("Logitech G435 Lightspeed","Logitech",7995,None)],
 "Monitors": [("LG 24MP60G 24-inch","LG",11999,10999),("Samsung 24-inch Monitor","Samsung",12999,None),("Acer Nitro VG240Y","Acer",13999,12499),("Dell S2421HN","Dell",14999,None),("ASUS TUF Gaming Monitor","ASUS",18999,16999)],
 "Webcams": [("Logitech C270 HD Webcam","Logitech",2495,None),("Lenovo 300 FHD Webcam","Lenovo",3999,3499)],
 "Speakers": [("Logitech Z120 Speakers","Logitech",1495,None),("Creative Pebble 2.0","Creative",2999,2699)],
 "Storage": [("Samsung 980 1TB SSD","Samsung",8999,7999),("WD Blue SN580 1TB SSD","WD",7499,None)],
 "Memory": [("Corsair Vengeance 16GB DDR4","Corsair",3999,3499),("Kingston Fury 16GB DDR5","Kingston",5499,None)],
 "Accessories": [("Anker 7-in-1 USB-C Hub","Anker",4999,4499),("Portronics My Buddy Laptop Stand","Portronics",1299,None),("Logitech Studio Series Mouse Pad","Logitech",995,None),("Amazon Basics USB-C Cable","Amazon Basics",499,399)],
}
IMAGES = {
    "Lenovo IdeaPad Slim 5": "https://www.technolife.com/image/color_image_TLP-166146_8f8f8f_42fed79c-2e7f-4f1a-a602-b9828cff4cc8.png",
    "HP Pavilion 15": "https://microport.in/cdn/shop/files/7S4N6PA-1_T1682044771_5df324f7-a299-4ffa-9518-bca5713095ef.png?v=1687244306",
    "ASUS VivoBook 15": "https://in.store.asus.com/media/catalog/product/v/i/vivobook_15_x1504z_x1504v_product_photo_1b_quite_blue_05_1.jpg",
    "Dell Inspiron 15": "https://assets.mmsrg.com/isr/166325/c1/-/ASSET_MP_152455489/fee_786_587_png",
    "Acer Aspire 5": "https://www.firstshop.co.za/cdn/shop/files/nx-khfea-001-traditional-laptops-42899699957924.png?v=1685692014&width=1214",
    "Logitech K380": "https://bizweb.dktcdn.net/100/329/122/products/ban-phim-khong-day-logitech-k380-multi-device-920-007596.jpg?v=1682565114497",
    "Logitech MX Keys S": "https://resource.logitech.com/content/dam/logitech/en/products/keyboards/mx-keys-s/migration-assets-for-delorean-2025/gallery/mx-keys-s-top-view-graphite-ch.png",
    "Redragon K552": "https://tshop.r10s.jp/springtech/cabinet/552/imgrc0098156804.jpg?fitin=720%3A720",
    "HP Mechanical Gaming Keyboard": "https://os-jo.com/image/cache/catalog/products/Accessories/Keyboard/HP-GK100F-KB/GK100-1200x1200.jpg",
    "Keychron K2 Wireless": "https://mks.blr1.cdn.digitaloceanspaces.com/uploads/2021/03/K2-LED_RGB-jpeg.webp",
    "Logitech M331 Silent": "https://smb-padiumkm-images-public-prod.oss-ap-southeast-5.aliyuncs.com/product/image/26022024/631a7af57476cace454199b8/65dc16958da0e6ff50777c7c/ba07554c3aade0340f99f13bf71f48.jpg",
    "Logitech MX Master 3S": "https://service.pcconnection.com/images/inhouse/9B37F09F-8797-487D-AC6A-22DE83E9F43D.jpg",
    "Razer DeathAdder Essential": "https://media.pichau.com.br/media/catalog/product/cache/2f958555330323e505eba7ce930bdf27/r/z/rz01-03850100-r3m1.jpg",
    "HP 280 Wireless Mouse": "https://cdn.media.amplience.net/i/xcite/532756-01",
    "Redragon M808 Storm": "https://down-id.img.susercontent.com/file/69c90b062b67d5d9167d6478da4b963c",
    "Sony WH-CH520": "https://blog-imgs-163.fc2.com/w/a/t/watchmonoblog/SONY_WH-CH520_03.jpg",
    "JBL Tune 760NC": "https://bnwcollections.com/uploads/products/1699265115JBL%20Tune%20760NC-bnw-white_11zon.webp",
    "boAt Rockerz 450": "https://mudramart.com/cdn/shop/products/boat-rockerz-450-664928_1200x1200.jpg?v=1676548838",
    "HyperX Cloud II": "https://cdn.tet.lv/tetveikals-prd-images/full_size/products/kingston-hyperx-cloud-ii-black-red-austinas-8-62f4b56f22733.jpg.webp",
    "Logitech G435 Lightspeed": "https://cdn.shopify.com/s/files/1/0742/0683/9100/files/logitech_g435.jpg",
    "LG 24MP60G 24-inch": "https://img.mbizmarket.co.id/products/thumbs/800x800/2023/02/01/aaba36d386b3cfd284592780cf0be486.jpg",
    "Samsung 24-inch Monitor": "https://pulser.kz/gallery/images/image-by-item-and-alias?dirtyAlias=a83506bd74-2.jpg&item=Product25381",
    "Acer Nitro VG240Y": "https://down-ph.img.susercontent.com/file/7aaee24e3d6783826c418c3311e0eda8",
    "Dell S2421HN": "https://i.dell.com/is/image/DellContent/content/dam/images/products/electronics-and-accessories/dell/monitors/s-series/s2421hn/s2421hn-xfp-02-gy.psd?chrss=full&fmt=pjpg&hei=3244&imwidth=5000&pscan=auto&qlt=100%2C1&resMode=sharp2&scl=1&size=3232%2C3244&wid=3232",
    "ASUS TUF Gaming Monitor": "https://www.static-src.com/wcsstore/Indraprastha/images/catalog/full/catalog-image/97/MTA-164330178/asus_asus_monitor_led_gaming_tuf_vg249q1a_wide_screen_24-_inch_full06_r3zbq0s0.jpg",
    "Logitech C270 HD Webcam": "https://www.gigahertz.com.ph/cdn/shop/files/logitech-c270-720p-hd-webcam-logitech-gigahertz-365267.jpg?v=1731912908&width=1000",
    "Lenovo 300 FHD Webcam": "https://down-my.img.susercontent.com/file/2650777e870747814dd8cad14df02741",
    "Logitech Z120 Speakers": "https://lecgriffith.com.au/cdn/shop/products/resize_1.jpg?v=1584954360",
    "Creative Pebble 2.0": "https://vipasa.pe/2527-superlarge_default/parlante-creative-pebble-20-black-51mf1680aa000.jpg",
    "Samsung 980 1TB SSD": "https://d2g44tvvp35wo2.cloudfront.net/photo/global/2021/03/10/Samsung-NVMe-SSD-980_Front_DL.jpg",
    "WD Blue SN580 1TB SSD": "https://static.nb.com.ar/i/nb_DISCO-SSD-M.2-1TB-WD-BLUE-SN580-NVME_export_7236e0fe3a40f2186d3d430e23319d9f.jpg",
    "Corsair Vengeance 16GB DDR4": "https://i.ebayimg.com/images/g/5BUAAeSweXppVvaI/s-l1200.jpg",
    "Kingston Fury 16GB DDR5": "https://www.kingstonstore.com.br/cdn/shop/products/FuryDIMM2_b0b40db0-36ae-49f5-971f-d9f615a63462.jpg?v=1638915903&width=1445",
    "Anker 7-in-1 USB-C Hub": "https://th-live-01.slatic.net/p/31b1e73122e6293e9cc816c0dd4335d5.jpg",
    "Portronics My Buddy Laptop Stand": "https://m.media-amazon.com/images/S/aplus-media-library-service-media/1a9d9c92-f559-4370-8ca0-39d97529f051.__CR0%2C0%2C970%2C600_PT0_SX970_V1___.jpeg",
    "Logitech Studio Series Mouse Pad": "https://down-id.img.susercontent.com/file/45a61784feb3bb7fb5de06d72e0aff07",
    "Amazon Basics USB-C Cable": "https://m.media-amazon.com/images/I/51O8fl%2BLWzL.jpg",
}

class Command(BaseCommand):
    help = "Create the TechGear demo categories and sample products."
    def handle(self, *args, **options):
        count = 0
        try:
            manifest = json.loads((settings.BASE_DIR / "static" / "products" / "manifest.json").read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            manifest = {}
        for category_name, rows in DATA.items():
            category, _ = Category.objects.get_or_create(name=category_name, defaults={"description":f"Explore our {category_name.lower()} collection."})
            for name, brand, price, discount in rows:
                Product.objects.update_or_create(name=name, defaults={
                    "category":category,"brand":brand,"price":price,"discount_price":discount,
                    "image":manifest.get(name, IMAGES[name]),
                    "slug":slugify(name),"stock":12,"rating":"4.6","review_count":42,
                    "short_description":f"Reliable {category_name.lower()} from {brand}.",
                    "description":f"Meet the {name}, thoughtfully selected by TechGear Store for dependable everyday performance. Designed for work, entertainment and a setup that feels like yours.",
                    "is_featured":count < 8,"is_active":True,
                })
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Catalog ready: {count} products across {len(DATA)} categories."))
