# -*- coding: utf-8 -*-

from openerp import models, fields, api

# CIIU, ICA y CREE


class Ciiu(models.Model):
    _name = "ciiu"
    _description = "Lista CIIU, ICA y CREE"

    name = fields.Char(string="Codigo y Descripción", store=True, compute="_concat_name")
    code = fields.Char('Código', required=True)
    description = fields.Char('Descripción')
    parent = fields.Many2one('ciiu', 'Padre')
    type = fields.Char('Tipo', size=20, required=True)

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
            self.name = str(self.code) + ' - ' + str(self.description)
