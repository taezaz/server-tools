# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C):
#        2012-Today Serpent Consulting Services (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import models, api, fields, exceptions, _


class MassObject(models.Model):
    _name = "mass.object"

    name = fields.Char("Name", size=64, required=True, select=1)
    model_id = fields.Many2one(
        'ir.model', 'Model', required=True, select=1)
    field_ids = fields.Many2many(
        'ir.model.fields', 'mass_field_rel', 'mass_id', 'field_id',
        'Fields')
    ref_ir_act_window = fields.Many2one(
        'ir.actions.act_window', 'Sidebar Action', readonly=True,
        help="Sidebar action to make this template available on records \
                of the related document model")
    ref_ir_value = fields.Many2one(
        'ir.values', 'Sidebar Button', readonly=True,
        help="Sidebar button to open the sidebar action")
    model_ids = fields.Many2many('ir.model', string='Model List')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('Name must be unique!'))
    ]

    @api.multi
    @api.onchange('model_id')
    def onchange_model_id(self):
        for mass_object in self:
            if not mass_object.model_id:
                continue
            model_obj = self.env['ir.model']
            # Empty recs
            model_ids = model_obj
            model_ids += mass_object.model_id
            for model in mass_object.model_id._model._inherits.keys():
                model_ids += model_obj.search([('model', '=', model)])
            mass_object.model_ids = model_ids

    @api.multi
    def create_action(self):
        for mass_object in self:
            button_name = _('Mass Editing (%s)' % mass_object.name)
            src_obj = mass_object.model_id.model
            action = self.env['ir.actions.act_window'].create({
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'mass.editing.wizard',
                'src_model': src_obj,
                'view_type': 'form',
                'context': "{'mass_editing_object' : %d}" % (mass_object.id),
                'view_mode': 'form,tree',
                'target': 'new',
                'auto_refresh': 1,
            })
            value = self.env['ir.values'].create({
                'name': button_name,
                'model': src_obj,
                'key2': 'client_action_multi',
                'value': "ir.actions.act_window,%s" % action.id,
            })
            mass_object.write({
                'ref_ir_act_window': action.id,
                'ref_ir_value': value.id,
            })
        return True

    @api.multi
    def unlink_action(self):
        for mass_object in self:
            try:
                if mass_object.ref_ir_act_window:
                    mass_object.sudo().ref_ir_act_window.unlink()
                    pass
                if mass_object.ref_ir_value:
                    mass_object.sudo().ref_ir_value.unlink()
            except:
                raise exceptions.UserError(
                    _("Warning"),
                    _("Deletion of the action record failed."))
        return True

    @api.multi
    def unlink(self):
        self.unlink_action()
        return super(MassObject, self).unlink()

    @api.multi
    def copy(self, default=None, context=None):
        if default is None:
            default = {}
        default.update({'name': '', 'field_ids': []})
        return super(MassObject, self).copy(default, context=context)
