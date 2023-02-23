# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Midilaj (<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import _, models, fields, api
from odoo.exceptions import UserError,ValidationError,AccessError




class ResPartner(models.Model):
    _inherit = 'res.partner'

    unique_id = fields.Char(string='Unique Id', help="The Unique Sequence no", readonly=True,default='/')

    @api.model
    def create(self, values):
        res = super(ResPartner, self).create(values)
        company_seq = self.env.company
        if res.customer_rank >  0 and res.unique_id == '/':
            if company_seq.next_code:
                res.unique_id = company_seq.next_code
                res.name = '[' + str(company_seq.next_code) + ']' + str(res.name)
                company_seq.write({'next_code': company_seq.next_code + 1})
            else:
                res.unique_id = company_seq.customer_code
                res.name = '[' + str(company_seq.customer_code) + ']' + str(res.name)
                company_seq.write({'next_code': company_seq.customer_code + 1})
        return res

    @api.model
    def create(self, values):
        res = super(ResPartner, self).create(values)
        company_seq = self.env.company
        if res.customer_rank >  0 and res.unique_id == '/':
            if company_seq.next_code:
                res.unique_id = company_seq.next_code
                res.name = '[' + str(company_seq.next_code) + ']' + str(res.name)
                company_seq.write({'next_code': company_seq.next_code + 1})
            else:
                res.unique_id = company_seq.customer_code
                res.name = '[' + str(company_seq.customer_code) + ']' + str(res.name)
                company_seq.write({'next_code': company_seq.customer_code + 1})
        return res

class PartnerId(models.Model):
    _inherit = 'res.partner'

    location = fields.Many2many(comodel_name="location.location",string="Location")

    circuit_id = fields.Char(string='Circuit Id', help="The Unique Circuit Id", readonly=True, default='/')
    circuit_count = fields.Integer(compute="compute_count",)

    def compute_count(self):
        for record in self:
            record.circuit_count = self.env['sale.order'].search_count(
                [('partner_id', '=', self.id)])

    def get_circuits(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Circuits',
            'view_mode': 'tree',
            'res_model': 'sale.order',
            'domain': [('partner_id', '=', self.id)],
            # 'context': "{'create': False}"
        }
class SaleOrder(models.Model):
    _inherit = ["sale.order",]

    partner_id = fields.Many2one("res.partner",string="Partner")
    unique_ids = fields.Char(related="partner_id.unique_id",  string="Customer ID")
    circuit = fields.Char(string="Circuit ID"  )
    location_type = fields.Selection([("new", "New"), ("old", "Old")])
    new_circuit = fields.Boolean(string="New Circuit Id ?")
    location = fields.Many2one(comodel_name="location.location",string="Location")
    # related_location = fields.Char(string="Location", compute ='_get_location')
    related_location = fields.Char(string="Location", related ='location.location')
    related_partner = fields.Char(string="Partner", related="partner_id.name")
    # related_location = fields.Char(string="Location", compute ='_get_location')
    # cir = fields.Many2one(comodel_name="circuit.circuit",compute ='_get_circuit')
    cir = fields.Many2one(comodel_name="circuit.circuit")
    counter = fields.Integer()

    def action_confirm(self):
        for record in self :
            if record.location_type == 'new':
                seq = record.unique_ids + record.order_line.product_id.default_code + str(record.location.id)
                record.write({'circuit': seq})
                cir = self.env["circuit.circuit"].create(
                    {
                        "circuit": record.circuit,
                        "partner_id": record.partner_id.name,
                        "location": record.related_location,
                        "order": record.name,
                        "product_id": record.order_line.product_id.name,
                    }
                )
            else:
                if record.location_type == 'old':
                    if record.new_circuit == True:
                        record.counter += 1
                        # seq = 'CID/' + record.unique_ids + '/' + record.order_line.product_id.default_code + '/' + record.related_location
                        cuit = self.env['circuit.circuit'].search_count(
                            [('partner_id', '=', self.related_partner), ('location', '=', self.related_location),
                             ('product_id', '=', self.order_line.product_id.name)])
                        print("ZZZZZZZZZZZZZZZ",cuit)
                        if cuit :
                            print("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", record.counter)
                            # seq = 'CID/' + record.unique_ids + '/' + record.order_line.product_id.default_code + '/' + record.related_location + "/" + str(record.partner_id.circuit_count)
                            seq = record.unique_ids + record.order_line.product_id.default_code + str(record.location.id) + str(cuit)
                            int(record.counter)
                            # record.counter += 1
                            record.write({'circuit': seq})
                            cir = self.env["circuit.circuit"].create(
                                {
                                    "circuit": record.circuit,
                                    "partner_id": record.partner_id.name,
                                    "location": record.related_location,
                                    "order": record.name,
                                    "product_id": record.order_line.product_id.name,
                                    # "counter": record.counter,

                                }
                            )
                    else :
                        if record.new_circuit == False:
                            # if record.order_line.product_id == cir.product_id:

                                cuit = self.env['circuit.circuit'].search([('partner_id', '=', self.related_partner),('location', '=', self.related_location),('product_id', '=', self.order_line.product_id.name)])
                                if cuit :
                                    print("jjjjjjjjjjjjjjjjjjjjjj",cuit.circuit,self.partner_id.name,self.location.location)
                                    self.write({'circuit': cuit.circuit})
                                else:
                                    # raise ValidationError(_("Set or Generate Barcode or product !"))
                                    raise UserError("Circuit_ID Not Found !!")
                                    # return {
                                    #     'warning': {'title': _('Warning'), 'message': _('Message needed.'), },
                                    # }
        super(SaleOrder, self).action_confirm()


class CircuitId(models.Model):
    _name = "circuit.circuit"
    _rec_name = "circuit"
    _sql_constraints = [
        ('circuit', 'unique(circuit)', "The Circuit ID already exists for this Customer with this Location . Circuit ID must be unique! "),
    ]

    circuit = fields.Char(string="Circuits")
    partner_id = fields.Char(string="Partner")
    location = fields.Char(string="Location")
    order = fields.Char(string="Order")
    order_id = fields.Many2one(comodel_name="sale.order",string="Order")
    # product_id = fields.Many2one(comodel_name="sale.order.line",string="product",related="product_id.product_id")
    product_id = fields.Char(string="Product")
    old_circuit_id = fields.Char(string='Old Circuit Id')
    counter = fields.Char()


class Location(models.Model):
    _name = "location.location"
    _rec_name = "location"
    # _inherit = 'res.partner'

    location = fields.Char(string="Location")
    partner_id = fields.Many2one(comodel_name="res.partner",string="Partner")
    # circuit_id = fields.Many2one(scomodel_name="sale.order",related="circuit_id.circuit",string="C")