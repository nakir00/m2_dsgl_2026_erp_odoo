from datetime import date, datetime

from odoo import Command
from odoo.tests.common import TransactionCase


class TestCashReport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.medicament = cls.env['pharmacie.medicament'].create({
            'nom_commercial': 'Medicament de test',
            'prix_achat': 100.0,
            'prix_vente': 150.0,
        })

    def test_bilan_inclut_les_ventes_de_la_fin_de_journee(self):
        jour_bilan = date(2026, 9, 20)
        self.env['pharmacie.vente'].create({
            'statut': 'confirmee',
            'date_vente': datetime(2026, 9, 20, 23, 59, 59),
            'ligne_ids': [Command.create({
                'medicament_id': self.medicament.id,
                'quantite': 2.0,
                'prix_unitaire': 150.0,
            })],
        })
        self.env['pharmacie.vente'].create({
            'statut': 'confirmee',
            'date_vente': datetime(2026, 9, 21, 0, 0, 0),
            'ligne_ids': [Command.create({
                'medicament_id': self.medicament.id,
                'quantite': 1.0,
                'prix_unitaire': 150.0,
            })],
        })

        bilan = self.env['pharmacie.bilan.caisse.wizard'].create({
            'date_debut': jour_bilan,
            'date_fin': jour_bilan,
        })

        self.assertEqual(bilan.nombre_ventes, 1)
        self.assertEqual(bilan.ca_total, 354.0)
