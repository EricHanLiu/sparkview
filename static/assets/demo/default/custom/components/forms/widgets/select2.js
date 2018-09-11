let removeInput = function (iid) {
    $("#row-" + iid).remove();
};

let spawnInput = function (iid, account_name) {
    $('#budget_container_' + iid).append('<div class="row no-gutters align-items-center" id="row-' + iid + '">' +
        '<div class="col-md-8">' +
        '<input type="number" id="' + iid + '" name="aw_budget_' + iid + '" ' +
        'class="form-control m-input m-input--air" placeholder="Budget for ' + account_name + ' ">' +
        '</div>' +
        '<div class="col-md-4">' +
        '<select class="form-control m-input" name="network_type_' + iid + '" id="network_type_' + iid + '" >' +
        '<option value="All">All</option>' +
        '<option value="Cross-network">Cross-network</option>' +
        '<option value="Search Network">Search</option>' +
        '<option value="Display Network">Display</option>' +
        '<option value="YouTube Search">Youtube Search</option>' +
        '<option value="YouTube Videos">Youtube Videos</option>' +
        '<option value="NOT_RELATED">Not related</option>' +
        '</select>' +
        '</div>' +
        '</div>');
};

var Select2 = function () {
    var e = function () {

        let checkbox = $('#m_gts_check');

        $("#select_analyser").select2({
            placeholder: 'Search account...'
        });

        $("#select_admin_report").select2({
            placeholder: 'Select report...'
        });

        $("#select_report").select2({
            placeholder: 'Select report...'
        });

        $("#select_report").on('select2:select', function (e) {
            let report = $("#select_report").val();
            let channel = $("#select_report").find(":selected").data("channel");
            let account_id = $("#select_report").find(":selected").data("account_id");
            window.location.href = '/tools/ppcanalyser/account/' + report + '/' + account_id + '/' + channel;
        });

        $("#select_analyser").on('select2:select', function (e) {
            let account_id = $("#select_analyser").val();
            let channel = $("#select_analyser").find(":selected").data("channel");
            window.location.href = '/tools/ppcanalyser/account/overview/' + account_id + '/' + channel;
        });

        $("#select_admin_report").on('select2:select', function (e) {

            var table = $("#m_admin_report");
            var table_wrapper = $('#report_results');
            var report = $(this).val();
            $('#report_results').removeClass('hidden');

            var columns = function (data) {
                let c = (data['report'] === 'changehistory') ? [{
                    "title": "Account",
                    "data": 'account',
                },
                    {
                        "title": data['column'],
                        "data": 'data_score',
                        "type": 'num',
                        "render": function (data, type, row, meta) {
                            if (type === 'display') {
                                data = '<a href="' + data.url + '">' + data.score + '</a>';
                            } else if (type === 'sort') {
                                data = data.score;
                            }
                            return data;
                        }
                    },
                    {
                        "title": data['column2'],
                        "data": 'last_change',
                        "type": 'num',
                        "render": function(data, type, row, meta){
                            return data;
                        }
                    }] : [
                    {
                        "title": "Account",
                        "data": 'account',
                    },
                    {
                        "title": data['column'],
                        "data": 'data_score',
                        "type": 'num',
                        "render": function (data, type, row, meta) {
                            if (type === 'display') {
                                data = '<a href="' + data.url + '">' + data.score + '</a>';
                            } else if (type === 'sort') {
                                data = data.score;
                            }
                            return data;
                        }
                    }
                ];

                return c
            };

            $.ajax({
                url: "/tools/ppcanalyser/reports/get",
                data: {
                    'report': report
                },
                type: 'GET',

                success: function (data) {

                    if ($.fn.DataTable.fnIsDataTable(table)) {
                        table.DataTable().clear();
                        table.DataTable().destroy();
                        table.remove();
                        table_wrapper.append('<table id="m_admin_report"><tbody></tbody></table>');

                        $("#m_admin_report").DataTable({
                            bDestroy: true,
                            bProcessing: false,
                            pageLength: 25,
                            aaData: data.table,
                            aoColumns: columns(data),
                            aaSorting: [[1, "asc"]]
                        });
                    } else {
                        table.DataTable({
                            bDestroy: true,
                            pageLength: 25,
                            aaData: data.table,
                            aoColumns: columns(data),
                            aaSorting: [[1, "asc"]],
                        });
                    }
                }
            });
        });

        $("#m_select2_adwords").select2({
            placeholder: "Search..."
        });

        $("#m_select2_adwords_am").select2({
            placeholder: "Search..."
        });

        $("#m_select2_bing_am").select2({
            placeholder: "Search..."
        });

        $("#m_select2_facebook_am").select2({
            placeholder: "Search..."
        });

        $("#m_select2_adwords_cm2").select2({
            placeholder: "Search..."
        });

        $("#m_select2_adwords_cm3").select2({
            placeholder: "Search..."
        });

        $("#m_select2_bing").select2({
            placeholder: "Search..."
        });

        $("#m_select2_bing_cm2").select2({
            placeholder: "Search..."
        });

        $("#m_select2_bing_cm3").select2({
            placeholder: "Search..."
        });

        $("#m_select2_facebook").select2({
            placeholder: "Search..."
        });

        $("#m_select2_facebook_cm2").select2({
            placeholder: "Search..."
        });

        $("#m_select2_facebook_cm3").select2({
            placeholder: "Search..."
        });

        $('#m_select2_adwords').on('select2:select', function (e) {

            if (!checkbox.prop('checked')) {

                let data = e.params.data;
                let iid = data.id;
                iid = iid.split('|');

                let budget_inputs = '<div class="budget-container" id="budget_container_' + iid[0] + '">' +
                    '<div class="row no-gutters align-items-center">' +
                    '<div class="col-md-12">' +
                    '<input type="number" id="' + iid[0] + '" name="aw_budget_' + iid[0] + '" ' +
                    'class="form-control m-input m-input--air" placeholder="Budget for ' + data.text + ' ">' +
                    '<div style="right: 20px;position: absolute;top: 8px;">' +
                    '<label class="m-checkbox">' +
                    '<input type="checkbox" name="networks" value="All" checked>' +
                    'All' +
                    '<span></span>' +
                    '</label>' +
                    '</div>' +
                    '</div>' +
                    // '<div class="col-md-1">' +
                    // '<i class="fa fa-plus-circle" style="margin-left: 20px" onclick="spawnInput(' + iid[0] + ',  \'' + data.text + '\')"></i>' +
                    // '</div>' +
                    // '<div class="col-md-1">' +
                    // '<i class="fa fa-minus-circle" style="margin-left: 20px" onclick="removeInput(' + iid[0] + ')"></i>' +
                    // '</div>' +
                    '</div>' +
                    '<div class="m-divider">' +
                    '<span></span>' +
                    '<span>or</span>' +
                    '<span></span>' +
                    '</div>' +
                    '<div class="m-checkbox-inline">\n' +
                    '<label class="m-checkbox">' +
                    '<input type="checkbox" name="networks" value="Cross-network"> Cross-network' +
                    '<span></span>' +
                    '</label>' +
                    '<label class="m-checkbox">' +
                    '<input type="checkbox" name="networks" value="Search Network"> Search' +
                    '<span></span>' +
                    '</label>' +
                    '<label class="m-checkbox">' +
                    '<input type="checkbox" name="networks" value="Display Network"> Display' +
                    '<span></span>' +
                    '</label>' +
                    '<label class="m-checkbox">' +
                    '<input type="checkbox" name="networks" value="Youtube Search"> Youtube Search' +
                    '<span></span>' +
                    '</label>' +
                    '<label class="m-checkbox">' +
                    '<input type="checkbox" name="networks" value="Youtube Videos"> Youtube Videos' +
                    '<span></span>' +
                    '</label>' +
                    '</div>' +
                    // '<div class="m-separator"></div>' +
                    '</div>';

                $('#budget-fields').append(budget_inputs);
            }
        });

        $('#m_select2_adwords').on('select2:unselect', function (e) {

            var data = e.params.data;
            let iid = data.id;
            iid = iid.split('|');
            $("#" + iid[0]).remove();
            $("#budget_container_" + iid[0]).remove();
        });

        $('#m_select2_bing').on('select2:select', function (e) {

            if (!checkbox.prop('checked')) {
                var data = e.params.data;
                let iid = data.id;
                iid = iid.split('|');
                $('#budget-fields-bing').append('' +
                    '<div class="budget-container" id="budget_container_' + iid[0] + '">' +
                    '<input type="number" id="' + iid[0] + '" name="bing_budget_' + iid[0] + '" ' +
                    'class="form-control m-input m-input--air" placeholder="Budget for ' + data.text + ' ">' +
                    '</div>');
            }
        });

        $('#m_select2_bing').on('select2:unselect', function (e) {

            var data = e.params.data;
            let iid = data.id;
            iid = iid.split('|');
            $("#budget_container_" + iid[0]).remove();
        });

        $('#m_select2_facebook').on('select2:select', function (e) {

                if (!checkbox.prop('checked')) {

                    var data = e.params.data;
                    let iid = data.id;
                    iid = iid.split('|');

                    $('#budget-fields-facebook').append('' +
                        '<div class="budget-container" id="budget_container_' + iid[0] + '">' +
                        '<input type="number" id="' + iid[0] + '" name="facebook_budget_' + iid[0] + '" ' +
                        'class="form-control m-input m-input--air" placeholder="Budget for ' + data.text + ' ">' +
                        '</div>');
                }
            }
        );

        $('#m_select2_facebook').on('select2:unselect', function (e) {

            var data = e.params.data;
            let iid = data.id;
            iid = iid.split('|');
            $("#budget_container_" + iid[0]).remove();
        });

        $("#m_select2_campaigns").select2({
            placeholder: "Search..."
        });

        $("#select_adwords").select2({
            placeholder: "Search accounts..."
        });

        $("#select_adwords2").select2({
            placeholder: "Search accounts..."
        });

        $("#select_adwords3").select2({
            placeholder: "Search accounts..."
        });

        $("#select_adwords4").select2({
            placeholder: "Search accounts..."
        });

        $("#select_adwords5").select2({
            placeholder: "Search accounts..."
        });

        $("#select_adwords6").select2({
            placeholder: "Search accounts..."
        });

        $("#select_adgroups").select2({
            placeholder: "Search adgroups..."
        });

        $("#select_adgroups2").select2({
            placeholder: "Search adgroups..."
        });

        $("#select_adgroups2").on('select2:select', function () {
            let ag_labels = $("#ag_labels_content");
            ag_labels.empty();

            let acc_id = $("#select_adwords6").val();
            let cmp_id = $("#select_campaigns4").val();
            let ag_id = $("#select_adgroups2").val();

            let data = {
                'account_id': acc_id,
                'campaign_id': cmp_id,
                'adgroup_id': ag_id,
            };

            $.ajax({
                url: "/tools/labels/get_labels",
                data: data,
                type: 'GET',

                success: function (data) {
                    for (var i = 0; i < data['labels'].length; i++) {
                        let label_name = data['labels'][i]['fields']['name'];
                        let label_id = data['labels'][i]['fields']['label_id'];

                        let new_label = '' +
                            '<span class="m-badge m-badge--success m-badge--wide" id="' + label_id + '-' + ag_id + '">' +
                            '' + label_name + ' <i class="fa fa-trash" onclick="deassignAdGroupLabel(' + acc_id + ', ' + label_id + ', ' + ag_id + ')"></i>\n' +
                            '</span> ';

                        ag_labels.append(new_label);
                    }
                }

            });
        });

        $("#select_adwords3").on('select2:select', function (e) {

            let select_campaigns = $("#select_campaigns");
            let select_labels = $("#select_labels2");


            select_campaigns.empty().trigger('change');
            select_labels.empty().trigger('change');

            let acc_id = $("#select_adwords3").val();
            let data = {
                'account_id': acc_id,
            };

            $.ajax({
                url: "/tools/labels/get_campaigns",
                data: data,
                type: 'GET',

                success: function (data) {

                    for (var i = 0; i < data['campaigns'].length; i++) {
                        let campaign_name = data['campaigns'][i]['fields']['campaign_name'];
                        let campaign_id = data['campaigns'][i]['fields']['campaign_id'];

                        var new_option = new Option(campaign_name, campaign_id, false, false);
                        select_campaigns.append(new_option).trigger('change');
                    }

                    for (var j = 0; j < data['text_labels'].length; j++) {
                        let label_name = data['text_labels'][j]['fields']['name'];
                        let label_id = data['text_labels'][j]['fields']['label_id'];

                        var new_label = new Option(label_name, label_id, false, false);
                        select_labels.append(new_label).trigger('change');
                    }
                }

            });

        });

        $("#select_adwords4").on('select2:select', function (e) {

            let select_campaigns = $("#select_campaigns2");
            let select_labels = $("#select_labels3");


            select_campaigns.empty().trigger('change');
            select_labels.empty().trigger('change');

            let acc_id = $("#select_adwords4").val();
            let data = {
                'account_id': acc_id,
            };

            $.ajax({
                url: "/tools/labels/get_campaigns",
                data: data,
                type: 'GET',

                success: function (data) {

                    for (var i = 0; i < data['campaigns'].length; i++) {
                        let campaign_name = data['campaigns'][i]['fields']['campaign_name'];
                        let campaign_id = data['campaigns'][i]['fields']['campaign_id'];

                        var new_option = new Option(campaign_name, campaign_id, false, false);
                        select_campaigns.append(new_option).trigger('change');
                    }

                    for (var j = 0; j < data['text_labels'].length; j++) {
                        let label_name = data['text_labels'][j]['fields']['name'];
                        let label_id = data['text_labels'][j]['fields']['label_id'];

                        var new_label = new Option(label_name, label_id, false, false);
                        select_labels.append(new_label).trigger('change');
                    }
                }

            });

        });

        $("#select_adwords5").on('select2:select', function (e) {

            let select_campaigns = $("#select_campaigns3");
            let select_labels = $("#select_labels3");


            select_campaigns.empty().trigger('change');
            select_labels.empty().trigger('change');

            let acc_id = $("#select_adwords5").val();
            let data = {
                'account_id': acc_id,
            };

            $.ajax({
                url: "/tools/labels/get_campaigns",
                data: data,
                type: 'GET',

                success: function (data) {
                    var new_ = new Option('', '', false, false);
                    select_campaigns.append(new_).trigger('change');
                    for (var i = 0; i < data['campaigns'].length; i++) {
                        let campaign_name = data['campaigns'][i]['fields']['campaign_name'];
                        let campaign_id = data['campaigns'][i]['fields']['campaign_id'];

                        var new_option = new Option(campaign_name, campaign_id, false, false);
                        select_campaigns.append(new_option).trigger('change');
                    }

                    for (var j = 0; j < data['text_labels'].length; j++) {
                        let label_name = data['text_labels'][j]['fields']['name'];
                        let label_id = data['text_labels'][j]['fields']['label_id'];

                        var new_label = new Option(label_name, label_id, false, false);
                        select_labels.append(new_label).trigger('change');
                    }
                }

            });

        });

        $("#select_adwords6").on('select2:select', function (e) {

            let select_campaigns = $("#select_campaigns4");

            select_campaigns.empty().trigger('change');

            let acc_id = $("#select_adwords6").val();
            let data = {
                'account_id': acc_id,
            };

            $.ajax({
                url: "/tools/labels/get_campaigns",
                data: data,
                type: 'GET',

                success: function (data) {
                    var new_ = new Option('', '', false, false);
                    select_campaigns.append(new_).trigger('change');
                    for (var i = 0; i < data['campaigns'].length; i++) {
                        let campaign_name = data['campaigns'][i]['fields']['campaign_name'];
                        let campaign_id = data['campaigns'][i]['fields']['campaign_id'];

                        var new_option = new Option(campaign_name, campaign_id, false, false);
                        select_campaigns.append(new_option).trigger('change');
                    }
                }
            });

        });

        $("#select_campaigns").select2({
            placeholder: "Search campaigns..."
        });

        $("#select_campaigns2").select2({
            placeholder: "Search campaigns..."
        });

        $("#select_campaigns3").select2({
            placeholder: "Search campaigns..."
        });

        $("#select_campaigns2").on('select2:select', function () {

            let select_adgroups = $("#select_adgroups");
            select_adgroups.empty().trigger('change');

            let acc_id = $("#select_adwords4").val();
            let cmp_id = $("#select_campaigns2").val();

            let data = {
                'account_id': acc_id,
                'campaign_id': cmp_id
            };

            $.ajax({
                url: "/tools/labels/get_adgroups",
                data: data,
                type: 'GET',

                success: function (data) {
                    var new_ = new Option('', '', false, false);
                    select_adgroups.append(new_).trigger('change');
                    for (var i = 0; i < data['adgroups'].length; i++) {
                        let adgroup_name = data['adgroups'][i]['fields']['adgroup_name'];
                        let adgroup_id = data['adgroups'][i]['fields']['adgroup_id'];

                        var new_option = new Option(adgroup_name, adgroup_id, false, false);
                        select_adgroups.append(new_option).trigger('change');
                    }
                }

            });

        });

        $("#select_campaigns3").on('select2:select', function () {

            let cmp_labels = $("#labels_content");
            cmp_labels.empty();

            let acc_id = $("#select_adwords5").val();
            let cmp_id = $("#select_campaigns3").val();

            let data = {
                'account_id': acc_id,
                'campaign_id': cmp_id
            };

            $.ajax({
                url: "/tools/labels/get_labels",
                data: data,
                type: 'GET',

                success: function (data) {

                    for (var i = 0; i < data['labels'].length; i++) {
                        let label_name = data['labels'][i]['fields']['name'];
                        let label_id = data['labels'][i]['fields']['label_id'];

                        let new_label = '' +
                            '<span class="m-badge m-badge--success m-badge--wide" id="' + label_id + '-' + cmp_id + '">' +
                            '' + label_name + ' <i class="fa fa-trash" onclick="deassignCampaignLabel(' + acc_id + ', ' + label_id + ', ' + cmp_id + ')"></i>\n' +
                            '</span> ';

                        cmp_labels.append(new_label);
                    }
                }

            });

        });

        $("#select_campaigns4").select2({
            placeholder: "Search campaigns..."
        });

        $("#select_campaigns4").on('select2:select', function () {

            let select_adgroups = $("#select_adgroups2");
            select_adgroups.empty().trigger('change');

            let acc_id = $("#select_adwords6").val();
            let cmp_id = $("#select_campaigns4").val();

            let data = {
                'account_id': acc_id,
                'campaign_id': cmp_id
            };

            $.ajax({
                url: "/tools/labels/get_adgroups",
                data: data,
                type: 'GET',

                success: function (data) {
                    var new_ = new Option('', '', false, false);
                    select_adgroups.append(new_).trigger('change');
                    for (var i = 0; i < data['adgroups'].length; i++) {
                        let adgroup_name = data['adgroups'][i]['fields']['adgroup_name'];
                        let adgroup_id = data['adgroups'][i]['fields']['adgroup_id'];

                        var new_option = new Option(adgroup_name, adgroup_id, false, false);
                        select_adgroups.append(new_option).trigger('change');
                    }
                }

            });

        });

        $("#select_labels").select2({
            placeholder: "Search labels..."
        });

        $("#select_labels2").select2({
            placeholder: "Search labels..."
        });

        $("#select_labels3").select2({
            placeholder: "Search labels..."
        });

        $("#select_accounts_cgr").select2({
            placeholder: "Select account..."
        });

        $("#select_accounts_cgr").on('select2:select', function (e) {

            let select_campaigns = $("#campaigns_gr_across");

            select_campaigns.empty().trigger('change');
            $('#gr_manual_across').prop('checked', false);
            $('#gr_text_across').prop('checked', false);
            $('#cgr_fdate_across').prop('checked', false);
            $(select_campaigns.data('select2').$container).addClass('hidden');
            $("#cgr_group_by_text").remove();
            $("#cgr_flight_date_across").addClass('hidden');

            $('#m_add_campaign_group_across').find('input[name=cgr_channel]').val(
                $("#select_accounts_cgr").find(':selected').data('channel')
            );


        });
    };
    return {
        init: function () {
            e()
        }
    }
}
();
jQuery(document).ready(function () {
    Select2.init()
});
