from datetime import date

from odoo import Command
from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase


class TestPartialReception(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fournisseur = cls.env['res.partner'].create({
            'name': 'Fournisseur de test',
            'is_fournisseur_pharma': True,
        })
        cls.medicament = cls.env['pharmacie.medicament'].create({
            'nom_commercial': 'Médicament de test',
            'prix_achat': 100.0,
            'prix_vente': 150.0,
        })

    def _create_reappro(self, quantite=10.0):
        reappro = self.env['pharmacie.reappro'].create({
            'fournisseur_id': self.fournisseur.id,
            'ligne_ids': [Command.create({
                'medicament_id': self.medicament.id,
                'quantite': quantite,
                'prix_unitaire': 100.0,
            })],
        })
        reappro.action_commander()
        return reappro

    def _receive(self, reappro, quantite, numero_lot_fournisseur):
        wizard = self.env['pharmacie.reappro.reception.wizard'].with_context(
            active_model='pharmacie.reappro', active_id=reappro.id).create({})
        wizard_line = wizard.ligne_ids
        wizard_line.write({
            'quantite_a_recevoir': quantite,
            'numero_lot_fournisseur': numero_lot_fournisseur,
            'date_fabrication': date(2026, 1, 1),
            'date_reception': date(2026, 2, 1),
            'date_peremption': date(2027, 1, 1),
        })
        wizard.action_valider()
        return reappro

    def test_reception_partielle_cree_des_lots_tracables(self):
        reappro = self._create_reappro()

        self._receive(reappro, 3.0, 'FOURN-001')
        self.assertEqual(reappro.statut, 'recue_partiellement')
        self.assertEqual(reappro.ligne_ids.quantite_recue, 3.0)
        self.assertEqual(reappro.ligne_ids.quantite_restante_a_recevoir, 7.0)
        first_lot = reappro.lot_ids
        self.assertEqual(first_lot.numero_lot_fournisseur, 'FOURN-001')
        self.assertEqual(first_lot.reappro_ligne_id, reappro.ligne_ids)
        self.assertEqual(first_lot.quantite_initiale, 3.0)

        self._receive(reappro, 7.0, 'FOURN-002')
        self.assertEqual(reappro.statut, 'recue')
        self.assertEqual(reappro.ligne_ids.quantite_recue, 10.0)
        self.assertEqual(reappro.ligne_ids.quantite_restante_a_recevoir, 0.0)
        self.assertEqual(len(reappro.lot_ids), 2)
        self.assertSetEqual(
            set(reappro.lot_ids.mapped('numero_lot_fournisseur')),
            {'FOURN-001', 'FOURN-002'},
        )

    def test_reception_refuse_une_quantite_superieure_au_reliquat(self):
        reappro = self._create_reappro()
        wizard = self.env['pharmacie.reappro.reception.wizard'].with_context(
            active_model='pharmacie.reappro', active_id=reappro.id).create({})
        wizard.ligne_ids.write({
            'quantite_a_recevoir': 11.0,
            'numero_lot_fournisseur': 'FOURN-003',
            'date_fabrication': date(2026, 1, 1),
            'date_reception': date(2026, 2, 1),
            'date_peremption': date(2027, 1, 1),
        })

        with self.assertRaises(UserError):
            wizard.action_valider()

        self.assertEqual(reappro.statut, 'commandee')
        self.assertFalse(reappro.lot_ids)

    def test_reception_est_reservee_au_gestionnaire(self):
        reappro = self._create_reappro()
        pharmacien = self.env['res.users'].with_context(
            no_reset_password=True).create({
                'name': 'Pharmacien de test',
                'login': 'pharmacien.reception.test',
                'groups_id': [Command.set([
                    self.env.ref(
                        'pharmacie_management.group_pharmacie_pharmacien').id,
                ])],
            })

        with self.assertRaises(AccessError):
            reappro.with_user(pharmacien).action_receptionner()
