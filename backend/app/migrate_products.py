import json
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

def migrate_products():
    db = SessionLocal()
    
    try:
        existing_products = db.query(models.Product).first()
        if existing_products:
            print("Products already exist in database")
            return
        
        product_categories_data = {
            'Gutscheine & Geschenkboxen': [
                {
                    'name': 'Gutschein Frauen CHF 20',
                    'description': 'Geschenkgutschein für Damen im Wert von CHF 20',
                    'detailed_description': 'Perfekt für kleinere Behandlungen oder als Ergänzung zu einem größeren Geschenk. Einlösbar für alle Dienstleistungen und Produkte.',
                    'usage': 'Im Salon einlösbar. Gültigkeitsdauer: 12 Monate ab Kaufdatum.',
                    'price': 'CHF 20',
                    'image': '/assets/voucher-women.jpg',
                    'category': 'Gutscheine & Geschenkboxen'
                },
                {
                    'name': 'Gutschein Frauen CHF 50',
                    'description': 'Geschenkgutschein für Damen im Wert von CHF 50',
                    'detailed_description': 'Ideal für Haarschnitte oder kleinere Colorationen. Einlösbar für alle Dienstleistungen und Produkte.',
                    'usage': 'Im Salon einlösbar. Gültigkeitsdauer: 12 Monate ab Kaufdatum.',
                    'price': 'CHF 50',
                    'image': '/assets/voucher-women.jpg',
                    'category': 'Gutscheine & Geschenkboxen'
                },
                {
                    'name': 'Gutschein Frauen CHF 100',
                    'description': 'Geschenkgutschein für Damen im Wert von CHF 100',
                    'detailed_description': 'Perfect für umfangreichere Behandlungen wie Colorationen oder Komplettbehandlungen. Einlösbar für alle Dienstleistungen und Produkte.',
                    'usage': 'Im Salon einlösbar. Gültigkeitsdauer: 12 Monate ab Kaufdatum.',
                    'price': 'CHF 100',
                    'image': '/assets/voucher-women.jpg',
                    'category': 'Gutscheine & Geschenkboxen'
                },
                {
                    'name': 'Geschenkbox (leer)',
                    'description': 'Elegante Geschenkbox zum Befüllen mit Produkten',
                    'detailed_description': 'Hochwertige Geschenkbox, die Sie mit Ihren Lieblingsprodukten befüllen können. Perfekt für individuelle Geschenke.',
                    'usage': 'Wählen Sie zusätzlich Ihre gewünschten Produkte aus.',
                    'price': 'CHF 5',
                    'image': '/assets/products/moisturizing-conditioner.jpg',
                    'category': 'Gutscheine & Geschenkboxen'
                }
            ],
            'Frauen Produkte': [
                {
                    'name': 'Trinity Curl Shampoo',
                    'description': 'Speziell für lockiges Haar entwickelt',
                    'detailed_description': 'Reinigt sanft und definiert Locken. Mit Gletscherwasser formuliert für optimale Lockenpflege und natürliche Sprungkraft.',
                    'usage': 'Auf das nasse Haar auftragen, sanft einmassieren und gründlich ausspülen.',
                    'price': 'CHF 32',
                    'image': '/assets/products/hydrating-shampoo.jpg',
                    'category': 'Frauen Produkte'
                },
                {
                    'name': 'Trinity Colour Shampoo',
                    'description': 'Farbschutz Shampoo für coloriertes Haar',
                    'detailed_description': 'Diese TRINITY haircare essentials Linie macht gefärbte Haare geschmeidig und lebhaft. Gletscherwasser, Granatapfel-Öl und Hagebutten-Extrakt schützen und stabilisieren die Haarfarbe.',
                    'usage': 'Auf das nasse Haar auftragen, sanft einmassieren und gründlich ausspülen.',
                    'price': 'CHF 34',
                    'image': '/assets/products/color-protect-shampoo.jpg',
                    'category': 'Frauen Produkte'
                },
                {
                    'name': 'Trinity Moisture Shampoo',
                    'description': 'Feuchtigkeitsspendendes Shampoo für den täglichen Gebrauch',
                    'detailed_description': 'Für den täglichen Gebrauch entwickelt. Gletscherwasser, Aloe Vera und Pro-Vitamin B5 versorgen das Haar intensiv mit Feuchtigkeit und geben ihm neuen Glanz und ein gesundes Aussehen.',
                    'usage': 'Auf das nasse Haar auftragen, sanft einmassieren und gründlich ausspülen.',
                    'price': 'CHF 30',
                    'image': '/assets/products/hydrating-shampoo.jpg',
                    'category': 'Frauen Produkte'
                }
            ],
            'Männer Produkte': [
                {
                    'name': 'Clay',
                    'description': 'Mattierende Styling-Creme mit festem Halt',
                    'detailed_description': 'TAILOR\'s Clay mit Bambus-Extrakt verleiht mattierende Textur und festen Halt. Perfekt für strukturierte, natürliche Looks ohne glänzendes Finish.',
                    'usage': 'Kleine Menge in den Handflächen verreiben und ins trockene oder leicht feuchte Haar einarbeiten. Nach Wunsch stylen.',
                    'price': 'CHF 32',
                    'image': '/lovable-uploads/42070e4c-5169-49b9-9c0b-f49470a8a11f.png',
                    'category': 'Männer Produkte'
                },
                {
                    'name': 'Cream',
                    'description': 'Styling-Creme für natürlichen Glanz',
                    'detailed_description': 'TAILOR\'s Cream mit Bambus-Extrakt bietet mittleren Halt mit natürlichem Glanz. Ideal für klassische und moderne Styles.',
                    'usage': 'Ins handtuchtrockene oder trockene Haar einarbeiten und stylen.',
                    'price': 'CHF 30',
                    'image': '/lovable-uploads/37f2682a-5140-4c84-9c39-622ba6610500.png',
                    'category': 'Männer Produkte'
                },
                {
                    'name': 'Daily Shampoo',
                    'description': 'Tägliche Reinigung für alle Haartypen',
                    'detailed_description': 'Das Daily Shampoo von TAILOR\'s reinigt das Haar sanft und gründlich. Die ausgewogene Formel eignet sich für die tägliche Anwendung und alle Haartypen.',
                    'usage': 'Ins nasse Haar einmassieren, aufschäumen und gründlich ausspülen.',
                    'price': 'CHF 26',
                    'image': '/assets/products/hydrating-shampoo.jpg',
                    'category': 'Männer Produkte'
                }
            ]
        }
        
        for category_name, products in product_categories_data.items():
            category = models.ProductCategory(name=category_name)
            db.add(category)
            db.commit()
            db.refresh(category)
            
            for product_data in products:
                product = models.Product(**product_data)
                db.add(product)
        
        db.commit()
        print(f"Successfully migrated {sum(len(products) for products in product_categories_data.values())} products")
        
    except Exception as e:
        print(f"Error migrating products: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_products()
