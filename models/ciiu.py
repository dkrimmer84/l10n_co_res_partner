# -*- coding: utf-8 -*-

from openerp import models, fields, api

# CIIU, ICA y CREE


class CiiuIcaCree(models.Model):
    _name = "lista.ciiu_ica_cree"
    _description = "Lista CIIU, ICA y CREE"

    name = fields.Char(string="Codigo y Descripción", store=True, compute="_concat_name")
    codigo = fields.Char('Código', required=True)
    description = fields.Char('Descripción')
    parent = fields.Many2one('lista.ciiu_ica_cree', 'Padre')
    type = fields.Char('Tipo', size=20, required=True)

    @api.one
    @api.depends('codigo', 'description')
    def _concat_name(self):
        """
        This function formats a new field in order to be able to search
        for CIIU as number or string
        @return: void
        """
        if self.codigo is False or self.description is False:
            self.name = ''
        else:
            self.name = str(self.codigo) + ' - ' + str(self.description)
