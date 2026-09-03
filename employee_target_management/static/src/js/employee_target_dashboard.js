/** @odoo-module **/

import {
    Component,
    onWillStart,
    onMounted,
    onWillUnmount,
    useState,
    useRef,
} from "@odoo/owl";

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";


export class EmployeeTargetDashboard extends Component {

    setup() {

        this.orm = useService("orm");

        // Chart references
        this.targetChartRef = useRef("targetChart");
        this.progressChartRef = useRef("progressChart");
        this.typeChartRef = useRef("typeChart");
        this.statusChartRef = useRef("statusChart");

        this.charts = {};

        this.state = useState({

            employeeId: false,
            periodId: false,
            targetTypeId: false,
            status: false,

            employees: [],
            periods: [],
            targetTypes: [],

            targets: [],

            totalTarget: 0,
            totalAchieved: 0,
            progress: 0,

            activeCount: 0,
            completedCount: 0,

        });


        onWillStart(async () => {

            await this.loadFilters();

            await this.loadDashboard();

        });


        onMounted(() => {

            this.renderCharts();

        });


        onWillUnmount(() => {

            this.destroyCharts();

        });

    }


    // ============================================================
    // LOAD FILTER DATA
    // ============================================================

    async loadFilters() {

        this.state.employees =
    await this.orm.call(
        "employee.target",
        "get_dashboard_employees",
        []
    );


        this.state.periods =
            await this.orm.searchRead(
                "employee.target.period",
                [],
                ["id", "name"],
                {
                    order: "id desc",
                }
            );


        this.state.targetTypes =
            await this.orm.searchRead(
                "employee.target.type",
                [],
                ["id", "name"],
                {
                    order: "name asc",
                }
            );

    }


    // ============================================================
    // LOAD TARGET DATA
    // ============================================================

    async loadDashboard() {

        const domain = [];


        if (this.state.employeeId) {

            domain.push([
                "employee_id",
                "=",
                this.state.employeeId,
            ]);

        }


        if (this.state.periodId) {

            domain.push([
                "period_id",
                "=",
                this.state.periodId,
            ]);

        }


        if (this.state.targetTypeId) {

            domain.push([
                "target_type_id",
                "=",
                this.state.targetTypeId,
            ]);

        }


        if (this.state.status) {

            domain.push([
                "status",
                "=",
                this.state.status,
            ]);

        }


        this.state.targets =
            await this.orm.searchRead(
                "employee.target",
                domain,
                [
                    "id",
                    "name",
                    "employee_id",
                    "target_type_id",
                    "period_id",
                    "target_value",
                    "achieved_value",
                    "progress",
                    "status",
                ]
            );


        this.calculateSummary();


        // Refresh charts after filters
        if (this.targetChartRef.el) {

            setTimeout(() => {

                this.renderCharts();

            }, 0);

        }

    }


    // ============================================================
    // SUMMARY
    // ============================================================

    calculateSummary() {

        let target = 0;

        let achieved = 0;

        let active = 0;

        let completed = 0;


        for (const record of this.state.targets) {

            target += record.target_value || 0;

            achieved += record.achieved_value || 0;


            if (record.status === "active") {

                active++;

            }


            if (record.status === "completed") {

                completed++;

            }

        }


        this.state.totalTarget = target;

        this.state.totalAchieved = achieved;


        this.state.progress =
            target > 0
                ? (achieved / target) * 100
                : 0;


        this.state.activeCount = active;

        this.state.completedCount = completed;

    }


    // ============================================================
    // DESTROY CHARTS
    // ============================================================

    destroyCharts() {

        for (const key in this.charts) {

            if (this.charts[key]) {

                this.charts[key].destroy();

            }

        }

        this.charts = {};

    }


    // ============================================================
    // RENDER ALL CHARTS
    // ============================================================

    renderCharts() {

        if (typeof Chart === "undefined") {

            console.error(
                "Employee Target Dashboard: Chart.js is not loaded."
            );

            return;

        }


        this.destroyCharts();


        this.renderTargetChart();

        this.renderProgressChart();

        this.renderTypeChart();

        this.renderStatusChart();

    }


    // ============================================================
    // TARGET VS ACHIEVED
    // ============================================================

    renderTargetChart() {

        const canvas =
            this.targetChartRef.el;


        if (!canvas) {
            return;
        }


        const employees = {};


        for (const record of this.state.targets) {

            const employee =
                record.employee_id
                    ? record.employee_id[1]
                    : "Unknown";


            if (!employees[employee]) {

                employees[employee] = {

                    target: 0,

                    achieved: 0,

                };

            }


            employees[employee].target +=
                record.target_value || 0;


            employees[employee].achieved +=
                record.achieved_value || 0;

        }


        const labels =
            Object.keys(employees);


        this.charts.target =
            new Chart(canvas, {

                type: "bar",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label: "Target",

                            data: labels.map(
                                employee =>
                                    employees[employee].target
                            ),

                        },

                        {

                            label: "Achieved",

                            data: labels.map(
                                employee =>
                                    employees[employee].achieved
                            ),

                        },

                    ],

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    scales: {

                        y: {

                            beginAtZero: true,

                        },

                    },

                },

            });

    }


    // ============================================================
    // EMPLOYEE PROGRESS
    // ============================================================

    renderProgressChart() {

        const canvas =
            this.progressChartRef.el;


        if (!canvas) {
            return;
        }


        const employees = {};


        for (const record of this.state.targets) {

            const employee =
                record.employee_id
                    ? record.employee_id[1]
                    : "Unknown";


            if (!employees[employee]) {

                employees[employee] = {

                    target: 0,

                    achieved: 0,

                };

            }


            employees[employee].target +=
                record.target_value || 0;


            employees[employee].achieved +=
                record.achieved_value || 0;

        }


        const labels =
            Object.keys(employees);


        const progress =
            labels.map(employee => {

                const item =
                    employees[employee];


                return item.target > 0

                    ? Math.min(
                        100,
                        (item.achieved / item.target) * 100
                    )

                    : 0;

            });


        this.charts.progress =
            new Chart(canvas, {

                type: "bar",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label: "Progress %",

                            data: progress,

                        },

                    ],

                },

                options: {

                    indexAxis: "y",

                    responsive: true,

                    maintainAspectRatio: false,

                    scales: {

                        x: {

                            beginAtZero: true,

                            max: 100,

                        },

                    },

                    plugins: {

                        legend: {

                            display: false,

                        },

                    },

                },

            });

    }


    // ============================================================
    // ACHIEVEMENT BY TARGET TYPE
    // ============================================================

    renderTypeChart() {

        const canvas =
            this.typeChartRef.el;


        if (!canvas) {
            return;
        }


        const types = {};


        for (const record of this.state.targets) {

            const type =
                record.target_type_id
                    ? record.target_type_id[1]
                    : "Unknown";


            if (!types[type]) {

                types[type] = 0;

            }


            types[type] +=
                record.achieved_value || 0;

        }


        const labels =
            Object.keys(types);


        this.charts.type =
            new Chart(canvas, {

                type: "bar",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label: "Achieved",

                            data: labels.map(
                                type => types[type]
                            ),

                        },

                    ],

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    scales: {

                        y: {

                            beginAtZero: true,

                        },

                    },

                },

            });

    }


    // ============================================================
    // STATUS DONUT
    // ============================================================

    renderStatusChart() {

        const canvas =
            this.statusChartRef.el;


        if (!canvas) {
            return;
        }


        const statuses = {

            draft: 0,

            submitted: 0,

            approved: 0,

            active: 0,

            completed: 0,

            cancelled: 0,

        };


        for (const record of this.state.targets) {

            if (
                statuses[record.status] !== undefined
            ) {

                statuses[record.status]++;

            }

        }


        const labels =
            Object.keys(statuses)
                .filter(
                    status =>
                        statuses[status] > 0
                );


        const values =
            labels.map(
                status =>
                    statuses[status]
            );


        this.charts.status =
            new Chart(canvas, {

                type: "doughnut",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            data: values,

                        },

                    ],

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            position: "bottom",

                        },

                    },

                },

            });

    }


    // ============================================================
    // FILTER EVENTS
    // ============================================================

    async onEmployeeChange(event) {

        this.state.employeeId =
            event.target.value
                ? parseInt(event.target.value)
                : false;

        await this.loadDashboard();

    }


    async onPeriodChange(event) {

        this.state.periodId =
            event.target.value
                ? parseInt(event.target.value)
                : false;

        await this.loadDashboard();

    }


    async onTargetTypeChange(event) {

        this.state.targetTypeId =
            event.target.value
                ? parseInt(event.target.value)
                : false;

        await this.loadDashboard();

    }


    async onStatusChange(event) {

        this.state.status =
            event.target.value || false;

        await this.loadDashboard();

    }


    async clearFilters() {

        this.state.employeeId = false;

        this.state.periodId = false;

        this.state.targetTypeId = false;

        this.state.status = false;

        await this.loadDashboard();

    }

}


EmployeeTargetDashboard.template =
    "employee_target_management.EmployeeTargetDashboard";


registry.category("actions").add(
    "employee_target_dashboard",
    EmployeeTargetDashboard
);