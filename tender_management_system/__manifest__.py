{
    "name": "Tender Management System",
    "summary": "Manage tenders, bids, and procurement seamlessly",
    "category": "Purchases",
    "version": "18.0.1.0.0",
    "depends": [
        "base",
        "mail",
        "web",
        "website",
        "portal",
        "sale",
        "purchase",
    ],
    "author": "Mantu Raj",
    "description": """
Tender Management System
========================

This module provides a complete system to manage tenders and bids within Odoo.  
It helps businesses streamline procurement by publishing tenders, inviting bids, evaluating suppliers, and selecting winners.

Key Features
------------
- Create and manage tenders
- Invite vendors and receive bids
- Track bid submissions and deadlines
- Automated sequence generation
- Portal access for suppliers to submit bids

    """,
    "data": [
        "data/sequence.xml",
        "data/tender_bid_form_data.xml",
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "views/tender_tender_views.xml",
        "views/tender_bid_views.xml",
        "views/purchase_portal_templates.xml",
        "views/menuitems.xml",
    ],
    "license": "LGPL-3",
    "images": [
        "static/description/icon.png",
    ],
    "application": True,
    "installable": True,
}
