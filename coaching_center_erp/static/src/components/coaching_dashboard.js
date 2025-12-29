/** @odoo-module */

import { registry } from "@web/core/registry"
import { useService } from "@web/core/utils/hooks"
import { Component, onWillStart,useState } from "@odoo/owl";

export class CoachingDashboard extends Component {

    async getTotalNumberOfTutor() {
        try {
            const result = await this.orm.call("coaching.tutor", "search_read", [[], ['state']]);
            let active = 0;
            let in_active = 0;  

            for (const res of result) {
                if (res.state === 'active') {
                    active++;
                } else if (res.state === 'inactive') {
                    in_active++;
                }
            }
    
            this.state.total_no_of_tutors = result.length;
            this.state.total_no_of_active_tutors = active;
            this.state.total_no_of_inactive_tutors = in_active;
        } catch (error) {
            console.error("Error fetching tutor details:", error);
        }
    }
    async getTotalNumberOfStudent() {
        try {
            const result = await this.orm.call("coaching.student", "search_read", [[], ['status']]);
            let active = 0;
            let in_active = 0;

            for (const res of result) {
                if (res.status === 'active') {
                    active++;
                } else if (res.status === 'left') {
                    in_active++;
                }
            }
            this.state.total_no_of_students = result.length;
            this.state.active_student = active;
            this.state.in_active_student = in_active;

        } catch (error) {
            console.error("Error fetching students details:", error);
        }
    }
    async getTotalNumberOfBatch() {
        try {
            const result = await this.orm.call("coaching.batch", "search_count", [[]]);
            this.state.total_no_of_batches = result;

        } catch (error) {
            console.error("Error fetching batches details:", error);
        }
    }

    async getTotalFeesDetails() {
        try {
        const fees = await this.orm.call("coaching.fee", "search_read", [[], ["amount", "amount_paid", "balance", "status"]]);

        let totalAmount = 0;
        let totalpaid = 0;
        let totalPending = 0;

        for (const fee of fees) {
            if (fee.status === 'paid') {
                totalpaid += fee.amount_paid || 0;
            }else if (fee.status === 'partial') {
                totalPending += fee.amount_paid || 0;
            }
        }
        
        totalAmount = totalpaid + totalPending;
        this.state.total_fee_amount = totalAmount;
        this.state.total_fees_paid = totalpaid;
        this.state.total_pending_balance = totalPending;
    } catch (error) {
        console.error("Error fetching fee stats:", error);
    }
    }
    
    async getBatchDetails() {
        try {
            const result = await this.orm.call("coaching.batch", "search_read", [[], ["name","student_count","total_amount_collected"]]);
            this.state.batch_details = result.map(batch => ({
                id: batch.id,
                name: batch.name,
                total_students: batch.student_count,
                amount_collected: batch.total_amount_collected,
            }));
            console.log("Batch Details:", this.state.batch_details);
            
        } catch (error) {
            console.error("Error fetching batch details:", error);
            this.state.batch_details = [];
        }
    }

    async getInquiryDetails() {
        try {
            const result = await this.orm.call("coaching.inquiry", "search_read", [[], ["status"]]);
            let total_inquiries = 0;
            let total_inquiries_follow_up = 0;
            let total_inquiries_register = 0;   
            for (const res of result) {
                total_inquiries++;
                if (res.status === 'followup') {
                    total_inquiries_follow_up++;
                } else if (res.status === 'registered') {
                    total_inquiries_register++;
                }
            }
            this.state.total_inquiries = result.length;
            this.state.followup_inquiries = total_inquiries_follow_up;
            this.state.registered_inquiries = total_inquiries_register;
            
        } catch (error) {
            console.error("Error fetching Inquiry details:", error);
        }
    }
    goToPreviousPage() {
        if (this.state.currentPage > 1) {
            this.state.currentPage -= 1;
        }
    }

    goToNextPage() {
        const maxPage = Math.ceil(this.state.batch_details.length / this.state.pageSize);
        if (this.state.currentPage < maxPage) {
            this.state.currentPage += 1;
        }
    }

    openTutorTreeView() {
        const base_url = window.location.origin;
        const action_id = "coaching_center_erp.action_coaching_tutor";
        const menu_id = "coaching_center_erp.menu_tutor";
        const project_url = `${base_url}/web#model=coaching.tutor&view_type=list&menu_id=${menu_id}&action=${action_id}`;

        window.location.href = project_url;
    }

    openStudentTreeView() {
        const base_url = window.location.origin;
        const action_id = "coaching_center_erp.action_coaching_student";
        const menu_id = "coaching_center_erp.menu_student";
        const contract_url = `${base_url}/web#model=coaching.student&view_type=list&menu_id=${menu_id}&action=${action_id}`;

        window.location.href = contract_url;
    }

    openBatchTreeView() {
        const base_url = window.location.origin;
        const action_id = "coaching_center_erp.action_coaching_batch";
        const menu_id = "coaching_center_erp.menu_batch";
        const contract_url = `${base_url}/web#model=coaching.batch&view_type=list&menu_id=${menu_id}&action=${action_id}`;

        window.location.href = contract_url;
    }

    openFeeTreeView() {
        const base_url = window.location.origin;
        const action_id = "coaching_center_erp.action_coaching_fee";
        const menu_id = "coaching_center_erp.menu_fee";
        const contract_url = `${base_url}/web#model=coaching.fee&view_type=list&menu_id=${menu_id}&action=${action_id}`;

        window.location.href = contract_url;
    }
    openInquiryTreeView() {
        const base_url = window.location.origin;
        const action_id = "coaching_center_erp.action_coaching_inquiry";
        const menu_id = "coaching_center_erp.menu_inquiry";
        const contract_url = `${base_url}/web#model=coaching.inquiry&view_type=list&menu_id=${menu_id}&action=${action_id}`;

        window.location.href = contract_url;
    }

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            currentPage: 1,
            pageSize: 5,
            batch_details: [],
        });
    
        onWillStart(async () => {
            await this.getTotalNumberOfTutor();
            await this.getTotalNumberOfStudent();
            await this.getTotalNumberOfBatch();
            await this.getTotalFeesDetails();
            await this.getBatchDetails();
            await this.getInquiryDetails();
        });
    }
}
CoachingDashboard.template = "Coaching_erp.CoachingDashboard"
registry.category("actions").add("coaching_center_erp.coaching_dashboard", CoachingDashboard)