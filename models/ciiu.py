# -*- coding: utf-8 -*-

from openerp import models, fields, api

# CIIU, ICA y CREE


class Ciiu(models.Model):
    _name = "ciiu"
    _description = "Lista CIIU, ICA y CREE"

    name = fields.Char(
        string="Codigo y Descripción",
        store=True,
        compute="_concat_name"
    )
    code = fields.Char('Código', required=True)
    description = fields.Char('Descripción', required=True)
    parent = fields.Many2one('ciiu', 'Padre')
    type = fields.Char(
        'Tipo',
        store=True,
        compute="_set_type"
    )
    hasParent = fields.Boolean('Tiene Padre?')

    @api.one
    @api.depends('code', 'description')
    def _concat_name(self):
        """
        This function concats two fields in order to be able to search
        for CIIU as number or string
        @return: void
        """
        if self.code is False or self.description is False:
            self.name = ''
        else:
            self.name = str(self.code) + ' - ' + str(self.description.encode('utf-8').strip())

    @api.one
    @api.depends('hasParent')
    def _set_type(self):
        """
        Parent and Child should be visually separated in the tree view.
        Therefore we tag them accordingly as 'view' or 'other'
        @return: void
        """
        # Parent
        if self.hasParent is True:
            self.type = 'view'
        # Child
        else:
            self.type = 'other'
