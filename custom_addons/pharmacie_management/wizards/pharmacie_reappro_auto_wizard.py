from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError


class PharmacieReapproAutoWizard(models.TransientModel):
    _name = 'pharmacie.reappro.auto.wizard'
    _description = "Réapprovisionnement automatique"

    ligne_ids = fields.One2many(
        'pharmacie.reappro.auto.wizard.ligne', 'wizard_id',
        string="Médicaments en alerte")

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        medicaments = self.env['pharmacie.medicament'].search([]).filtered(
            lambda m: m.stock_actuel <= m.alerte_rupture)
        vals['ligne_ids'] = [
            Command.create({
                'medicament_id': medicament.id,
                'fournisseur_id': medicament.fournisseur_id.id,
                'quantite_suggeree': max(
                    medicament.alerte_rupture * 2 - medicament.stock_actuel, 1),
            })
            for medicament in medicaments
        ]
        return vals

    def action_valider(self):
        self.ensure_one()
        if self.ligne_ids.filtered(lambda l: not l.fournisseur_id):
            raise UserError(_(
                "Chaque médicament doit avoir un fournisseur habituel pour "
                "générer un bon de commande."))

        reappro_ids = []
        for fournisseur in self.ligne_ids.fournisseur_id:
            lignes = self.ligne_ids.filtered(lambda l: l.fournisseur_id == fournisseur)
            # sudo() : le tableau ACL du sujet limite le Pharmacien à la
            # lecture des réappros, mais le wizard est explicitement décrit
            # comme un outil pharmacien pour générer des bons de commande.
            reappro = self.env['pharmacie.reappro'].sudo().create({
                'fournisseur_id': fournisseur.id,
                'ligne_ids': [
                    Command.create({
                        'medicament_id': ligne.medicament_id.id,
                        'quantite': ligne.quantite_suggeree,
                        'prix_unitaire': ligne.medicament_id.prix_achat,
                    })
                    for ligne in lignes
                ],
            })
            reappro_ids.append(reappro.id)

        return {
            'type': 'ir.actions.act_window',
            'name': _("Bons de commande générés"),
            'res_model': 'pharmacie.reappro',
            'view_mode': 'list,form',
            'domain': [('id', 'in', reappro_ids)],
        }


class PharmacieReapproAutoWizardLigne(models.TransientModel):
    _name = 'pharmacie.reappro.auto.wizard.ligne'
    _description = "Ligne du wizard de réapprovisionnement automatique"

    wizard_id = fields.Many2one(
        'pharmacie.reappro.auto.wizard', required=True, ondelete='cascade')
    medicament_id = fields.Many2one('pharmacie.medicament', string="Médicament", required=True)
    fournisseur_id = fields.Many2one('res.partner', string="Fournisseur habituel")
    quantite_suggeree = fields.Float(string="Quantité suggérée")
