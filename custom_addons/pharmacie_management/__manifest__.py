{
    'name': "Gestion de Pharmacie",
    'summary': "Catalogue, lots, ventes comptoir et réapprovisionnement pour une pharmacie",
    'description': """
Module de gestion de pharmacie pour Odoo 18 Community.

Fonctionnalités :
- Catalogue de médicaments (DCI, dosage, TVA, marge)
- Suivi des lots avec péremption
- Ventes au comptoir avec ou sans ordonnance
- Réapprovisionnement fournisseurs
- Sécurité par profil (vendeur, pharmacien, gestionnaire)
""",
    'author': "Équipe M2 DSGL 2026",
    'category': 'Inventory',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'web'],
    'data': [
        # Ordre de chargement à respecter au fur et à mesure des tickets :
        # 1. security/groups.xml
        'security/pharmacie_security.xml',
        # 2. security/ir.model.access.csv
        'security/ir.model.access.csv',
        # 3. security/record_rules.xml
        'security/record_rules.xml',
        # 4. data/*.xml
        'data/ir_sequence.xml',
        # 5. views/*.xml
        'views/res_partner_views.xml',
        'views/pharmacie_medicament_views.xml',
        'views/pharmacie_lot_views.xml',
        'views/pharmacie_ordonnance_views.xml',
        'views/pharmacie_vente_views.xml',
        'views/pharmacie_reappro_views.xml',
        # 6. wizards/*.xml
        'wizards/pharmacie_reappro_auto_wizard_views.xml',
        'wizards/pharmacie_bilan_caisse_wizard_views.xml',
        'views/pharmacie_menu.xml',
        # 7. reports/*.xml
        'report/ticket_caisse_report.xml',
        'report/inventaire_stock_report.xml',
        'report/bilan_caisse_report.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
}
