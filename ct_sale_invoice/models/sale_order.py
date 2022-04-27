from odoo import api, fields, models, _


class SaleInvoice(models.Model):
    _inherit = "sale.order.line"

    width = fields.Integer('width')
    length = fields.Integer('length')
    total = fields.Integer(string='total', compute='_compute_amount', store=True)

    @api.depends('length', 'width', 'price_unit')
    def _compute_amount(self):
        rec = super(SaleInvoice, self)._compute_amount()
        for res in self:
            res.total = res.length * res.width * res.product_uom_qty
            res.price_subtotal = res.total * res.price_unit

            res.amount_tax = ((res.price_subtotal * res.tax_id.amount) / 100.0)

    def invoice_line_create_vals(self, invoice_id, qty):

        rec = super(SaleInvoice, self).invoice_line_create_vals(invoice_id, qty)
        for line in self:
            for i in rec:
                i.update({'width': line.width, 'length': line.length, 'total': line.total})

        return rec


class Sale(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):

        super(Sale, self)._amount_all()
        for res in self:
            res.amount_tax = 0
            res.amount_total = 0

            for i in res.order_line:
                res.amount_tax += ((i.price_subtotal * i.tax_id.amount) / 100.0)
                res.amount_total += res.amount_untaxed + res.amount_tax


class AccountInvoice(models.Model):
    _inherit = "account.invoice.line"

    width = fields.Integer('width')
    length = fields.Integer('length')
    total = fields.Integer(string='total', compute='_compute_price', store=True)

    @api.one
    @api.depends('price_unit', 'length', 'width', 'price_subtotal', 'discount', 'discount_type', 'invoice_line_tax_ids',
                 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        quantity = 1.0
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                          partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            currency = self.invoice_id.currency_id
            date = self.invoice_id._get_currency_rate_date()
            price_subtotal_signed = currency._convert(price_subtotal_signed, self.invoice_id.company_id.currency_id,
                                                      self.company_id or self.env.user.company_id,
                                                      date or fields.Date.today())
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
        taxes = False
        if self._context.get('type', '') == 'out_invoice' and self.length and self.width:
            self.total = self.length * self.width * self.quantity
            self.price_subtotal = self.total * self.price_unit

            if self.discount_type == 'fixed':
                self.price = self.price_subtotal - self.discount or 0.0
                self.price_subtotal = self.price
            else:
                self.price = self.price_subtotal * self.discount / 100
                self.price_subtotal = self.price_subtotal - self.price
        else:
            if self.discount_type == 'fixed':
                self.price_subtotal = self.price_unit * self.quantity - self.discount or 0.0
            else:
               self.price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
               self.price_subtotal = self.price