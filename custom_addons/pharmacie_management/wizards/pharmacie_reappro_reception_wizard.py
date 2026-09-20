from odoo import Command, _, api, fields, models
from odoo.exceptions import AccessError, UserError


class PharmacieReapproReceptionWizard(models.TransientModel):
    _name = 'pharmacie.reappro.reception.wizard'
    _description = "Réception partielle de fournisseur"

    reappro_id = fields.Many2one(
        'pharmacie.reappro', string="Bon de commande", required=True, readonly=True)
    ligne_ids = fields.One2many(
        'pharmacie.reappro.reception.wizard.ligne', 'wizard_id',
        string="Lignes à réceptionner")

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        reappro = self.env['pharmacie.reappro'].browse(
            self.env.context.get('active_id'))
        if not reappro.exists():
            return vals
        if reappro.statut not in ('commandee', 'recue_partiellement'):
            raise UserError(_(
                "Seule une commande passée peut être réceptionnée."))

        vals.update({
            'reappro_id': reappro.id,
            'ligne_ids': [
                Command.create({
                    'reappro_ligne_id': line.id,
                    'quantite_a_recevoir': line.quantite_restante_a_recevoir,
                })
                for line in reappro.ligne_ids
                if line.quantite_restante_a_recevoir > 0
            ],
        })
        return vals

    def action_valider(self):
        self.ensure_one()
        if (not self.env.is_superuser()
                and not self.env.user.has_group(
                    'pharmacie_management.group_pharmacie_gestionnaire')):
            raise AccessError(_("Seul un gestionnaire peut valider une réception."))

        reappro = self.reappro_id
        if reappro.statut not in ('commandee', 'recue_partiellement'):
            raise UserError(_(
                "Ce bon de commande ne peut plus être réceptionné."))

        lignes_a_receptionner = self.ligne_ids.filtered(
            lambda line: line.quantite_a_recevoir > 0)
        if not lignes_a_receptionner:
            raise UserError(_("Saisissez au moins une quantité à réceptionner."))

        for line in lignes_a_receptionner:
            line._check_reception()

        for line in lignes_a_receptionner:
            reappro_line = line.reappro_ligne_id
            self.env['pharmacie.lot'].create({
                'medicament_id': reappro_line.medicament_id.id,
                'quantite_initiale': line.quantite_a_recevoir,
                'quantite_restante': line.quantite_a_recevoir,
                'prix_achat_lot': reappro_line.prix_unitaire,
                'numero_lot_fournisseur': line.numero_lot_fournisseur,
                'date_fabrication': line.date_fabrication,
                'date_reception': line.date_reception,
                'date_peremption': line.date_peremption,
                'reappro_id': reappro.id,
                'reappro_ligne_id': reappro_line.id,
            })

        reappro.statut = (
            'recue' if all(
                line.quantite_recue >= line.quantite for line in reappro.ligne_ids
            ) else 'recue_partiellement'
        )

        return {
            'type': 'ir.actions.act_window',
            'name': _("Bon de commande"),
            'res_model': 'pharmacie.reappro',
            'res_id': reappro.id,
            'view_mode': 'form',
            'target': 'current',
        }


class PharmacieReapproReceptionWizardLigne(models.TransientModel):
    _name = 'pharmacie.reappro.reception.wizard.ligne'
    _description = "Ligne de réception fournisseur"

    wizard_id = fields.Many2one(
        'pharmacie.reappro.reception.wizard', required=True, ondelete='cascade')
    reappro_ligne_id = fields.Many2one(
        'pharmacie.reappro.ligne', string="Ligne commandée", required=True, readonly=True)
    medicament_id = fields.Many2one(
        related='reappro_ligne_id.medicament_id', string="Médicament", readonly=True)
    quantite_commandee = fields.Float(
        related='reappro_ligne_id.quantite', string="Quantité commandée", readonly=True)
    quantite_deja_recue = fields.Float(
        related='reappro_ligne_id.quantite_recue', string="Déjà reçue", readonly=True)
    quantite_restante = fields.Float(
        related='reappro_ligne_id.quantite_restante_a_recevoir',
        string="Restante", readonly=True)
    quantite_a_recevoir = fields.Float(string="Quantité reçue maintenant")
    numero_lot_fournisseur = fields.Char(string="Numéro de lot fournisseur")
    date_fabrication = fields.Date(string="Date de fabrication")
    date_reception = fields.Date(
        string="Date de réception", default=fields.Date.context_today)
    date_peremption = fields.Date(string="Date de péremption")

    def _check_reception(self):
        self.ensure_one()
        if self.quantite_a_recevoir > self.quantite_restante:
            raise UserError(_(
                "La quantité reçue pour %(medicament)s dépasse le reliquat "
                "commandé (%(reliquat).2f)."
            ) % {
                'medicament': self.medicament_id.display_name,
                'reliquat': self.quantite_restante,
            })
        if not self.numero_lot_fournisseur:
            raise UserError(_(
                "Le numéro de lot fournisseur est obligatoire pour %(medicament)s."
            ) % self.medicament_id.display_name)
        if not all((self.date_fabrication, self.date_reception, self.date_peremption)):
            raise UserError(_(
                "Les dates de fabrication, réception et péremption sont obligatoires "
                "pour %(medicament)s."
            ) % self.medicament_id.display_name)
        if self.date_peremption <= self.date_fabrication:
            raise UserError(_(
                "La date de péremption doit être postérieure à la date de fabrication."
            ))
