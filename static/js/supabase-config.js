// Supabase Configuration for AIVIIZN Maintenance System
// Include this before your page scripts

const SUPABASE_CONFIG = {
    url: 'https://sejebqdhcilwcpjpznep.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ'
};

// Initialize Supabase client
const supabase = window.supabase.createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey);

// Utility functions for Supabase operations
const SupabaseUtils = {
    // Work Orders
    async getWorkOrders(page = 1, limit = 10, filters = {}) {
        let query = supabase
            .from('work_orders_with_details')
            .select('*')
            .order('created_at', { ascending: false });

        // Apply filters
        if (filters.status) {
            query = query.eq('status', filters.status);
        }
        if (filters.property) {
            query = query.ilike('property_name', `%${filters.property}%`);
        }
        if (filters.assignee) {
            query = query.ilike('assigned_to', `%${filters.assignee}%`);
        }
        if (filters.vendor) {
            query = query.ilike('vendor_name', `%${filters.vendor}%`);
        }

        // Apply pagination
        const from = (page - 1) * limit;
        const to = from + limit - 1;
        query = query.range(from, to);

        const { data, error, count } = await query;
        
        if (error) {
            console.error('Error fetching work orders:', error);
            return { data: [], count: 0, error };
        }
        
        return { data, count, error: null };
    },

    async createWorkOrder(workOrderData) {
        // First get property and unit IDs
        const { data: property } = await supabase
            .from('properties')
            .select('id')
            .eq('name', workOrderData.property)
            .single();

        let unitId = null;
        if (workOrderData.unit && property) {
            const { data: unit } = await supabase
                .from('units')
                .select('id')
                .eq('property_id', property.id)
                .eq('unit_number', workOrderData.unit)
                .single();
            unitId = unit?.id;
        }

        // Get vendor ID if specified
        let vendorId = null;
        if (workOrderData.vendor) {
            const { data: vendor } = await supabase
                .from('vendors')
                .select('id')
                .eq('name', workOrderData.vendor)
                .single();
            vendorId = vendor?.id;
        }

        const { data, error } = await supabase
            .from('work_orders')
            .insert({
                property_id: property?.id,
                unit_id: unitId,
                request_type: workOrderData.requestType,
                category: workOrderData.category,
                priority: workOrderData.priority,
                title: workOrderData.title,
                description: workOrderData.description,
                vendor_id: vendorId,
                assigned_to: workOrderData.assignedTo,
                scheduled_date: workOrderData.scheduledDate,
                scheduled_time: workOrderData.scheduledTime,
                entry_permission: workOrderData.entryPermission,
                notify_tenant: workOrderData.notifyTenant,
                allow_key_access: workOrderData.allowKeyAccess,
                entry_instructions: workOrderData.entryInstructions
            })
            .select()
            .single();

        return { data, error };
    },

    async updateWorkOrder(id, updates) {
        const { data, error } = await supabase
            .from('work_orders')
            .update(updates)
            .eq('id', id)
            .select()
            .single();

        return { data, error };
    },

    async deleteWorkOrder(id) {
        const { error } = await supabase
            .from('work_orders')
            .delete()
            .eq('id', id);

        return { error };
    },

    // Recurring Templates
    async getRecurringTemplates(page = 1, limit = 10, filters = {}) {
        let query = supabase
            .from('recurring_templates_with_details')
            .select('*')
            .order('created_at', { ascending: false });

        // Apply filters
        if (filters.status) {
            query = query.eq('status', filters.status);
        }
        if (filters.frequency) {
            query = query.eq('frequency', filters.frequency);
        }
        if (filters.category) {
            query = query.eq('category', filters.category);
        }
        if (filters.name) {
            query = query.ilike('template_name', `%${filters.name}%`);
        }

        // Apply pagination
        const from = (page - 1) * limit;
        const to = from + limit - 1;
        query = query.range(from, to);

        const { data, error } = await query;
        
        return { data: data || [], error };
    },

    async createRecurringTemplate(templateData) {
        // Get vendor ID if specified
        let vendorId = null;
        if (templateData.vendor) {
            const { data: vendor } = await supabase
                .from('vendors')
                .select('id')
                .eq('name', templateData.vendor)
                .single();
            vendorId = vendor?.id;
        }

        const { data, error } = await supabase
            .from('recurring_templates')
            .insert({
                template_name: templateData.templateName,
                frequency: templateData.frequency,
                interval_value: templateData.intervalValue,
                schedule_details: templateData.scheduleDetails,
                category: templateData.category,
                priority: templateData.priority,
                description: templateData.description,
                vendor_id: vendorId,
                auto_assign: templateData.autoAssign,
                notify_tenants: templateData.notifyTenants,
                require_entry_permission: templateData.requireEntryPermission,
                special_instructions: templateData.specialInstructions,
                next_generation_date: templateData.nextGenerationDate
            })
            .select()
            .single();

        // Add properties to template
        if (data && templateData.properties && templateData.properties.length > 0) {
            const { data: properties } = await supabase
                .from('properties')
                .select('id, name')
                .in('name', templateData.properties);

            if (properties && properties.length > 0) {
                const templateProperties = properties.map(prop => ({
                    template_id: data.id,
                    property_id: prop.id
                }));

                await supabase
                    .from('template_properties')
                    .insert(templateProperties);
            }
        }

        return { data, error };
    },

    async updateRecurringTemplate(id, updates) {
        const { data, error } = await supabase
            .from('recurring_templates')
            .update(updates)
            .eq('id', id)
            .select()
            .single();

        return { data, error };
    },

    async deleteRecurringTemplate(id) {
        const { error } = await supabase
            .from('recurring_templates')
            .delete()
            .eq('id', id);

        return { error };
    },

    // Inspections
    async getInspections(page = 1, limit = 10, filters = {}) {
        let query = supabase
            .from('inspections_with_details')
            .select('*')
            .order('scheduled_date', { ascending: false });

        // Apply filters
        if (filters.status) {
            query = query.eq('status', filters.status);
        }
        if (filters.type) {
            query = query.eq('inspection_type', filters.type);
        }
        if (filters.inspector) {
            query = query.ilike('inspector_name', `%${filters.inspector}%`);
        }
        if (filters.property) {
            query = query.ilike('property_name', `%${filters.property}%`);
        }

        // Apply pagination
        const from = (page - 1) * limit;
        const to = from + limit - 1;
        query = query.range(from, to);

        const { data, error } = await query;
        
        return { data: data || [], error };
    },

    async createInspection(inspectionData) {
        // First get property and unit IDs
        const { data: property } = await supabase
            .from('properties')
            .select('id')
            .eq('name', inspectionData.property)
            .single();

        let unitId = null;
        if (inspectionData.unit && property) {
            const { data: unit } = await supabase
                .from('units')
                .select('id')
                .eq('property_id', property.id)
                .eq('unit_number', inspectionData.unit)
                .single();
            unitId = unit?.id;
        }

        const { data, error } = await supabase
            .from('inspections')
            .insert({
                property_id: property?.id,
                unit_id: unitId,
                inspection_type: inspectionData.inspectionType,
                template_name: inspectionData.templateName,
                inspector_name: inspectionData.inspectorName,
                inspector_type: inspectionData.inspectorType,
                scheduled_date: inspectionData.scheduledDate,
                scheduled_time: inspectionData.scheduledTime,
                purpose: inspectionData.purpose,
                access_instructions: inspectionData.accessInstructions,
                notify_tenant: inspectionData.notifyTenant,
                require_permission: inspectionData.requirePermission,
                photo_documentation: inspectionData.photoDocumentation,
                auto_create_work_orders: inspectionData.autoCreateWorkOrders
            })
            .select()
            .single();

        return { data, error };
    },

    async updateInspection(id, updates) {
        const { data, error } = await supabase
            .from('inspections')
            .update(updates)
            .eq('id', id)
            .select()
            .single();

        return { data, error };
    },

    async deleteInspection(id) {
        const { error } = await supabase
            .from('inspections')
            .delete()
            .eq('id', id);

        return { error };
    },

    // Utility functions
    async getProperties() {
        const { data, error } = await supabase
            .from('properties')
            .select('*')
            .order('name');

        return { data: data || [], error };
    },

    async getVendors() {
        const { data, error } = await supabase
            .from('vendors')
            .select('*')
            .eq('is_active', true)
            .order('name');

        return { data: data || [], error };
    },

    async getUnitsForProperty(propertyName) {
        const { data, error } = await supabase
            .from('units')
            .select('unit_number, tenant_name')
            .eq('properties.name', propertyName);

        return { data: data || [], error };
    },

    // Dashboard metrics
    async getDashboardMetrics() {
        // Get work order metrics
        const { data: workOrderMetrics } = await supabase.rpc('get_work_order_metrics');
        
        // Get inspection metrics  
        const { data: inspectionMetrics } = await supabase.rpc('get_inspection_metrics');
        
        // Get template metrics
        const { data: templateMetrics } = await supabase.rpc('get_template_metrics');

        return {
            workOrders: workOrderMetrics || {},
            inspections: inspectionMetrics || {},
            templates: templateMetrics || {}
        };
    }
};

// Export for global use
window.SupabaseUtils = SupabaseUtils;