var DatatableChildDataLocalDemo = function() {
  var r = function(r) {
      $("<div/>").attr("id", "child_data_local_" + r.data.RecordID).appendTo(r.detailCell).mDatatable({
        data: {
          type: "local",
          source: r.data.Orders,
          pageSize: 10,
          saveState: {
            cookie: !0,
            webstorage: !0
          }
        },
        layout: {
          theme: "default",
          scroll: !0,
          height: 300,
          footer: !1,
          spinner: {
            type: 1,
            theme: "default"
          }
        },
        sortable: !0,
        columns: [{
          field: "OrderID",
          title: "Order ID",
          sortable: !1
        }, {
          field: "ShipCountry",
          title: "Country",
          width: 100
        }, {
          field: "ShipAddress",
          title: "Ship Address"
        }, {
          field: "ShipName",
          title: "Ship Name"
        }]
      })
    },
    e = function() {
      var e = JSON.parse('[{"RecordID":1,"FirstName":"Mariellen","LastName":"Goretti","Company":"Chatterpoint","Email":"mgoretti0@omniture.com","Orders":[{"OrderID":"65044-0847","ShipCountry":"CN","ShipAddress":"7770 Melody Plaza","ShipName":"Denesik Inc"},{"OrderID":"42747-224","ShipCountry":"CN","ShipAddress":"161 Nova Pass","ShipName":"Fritsch, Rau and Schamberger"},{"OrderID":"69031-001","ShipCountry":"MX","ShipAddress":"00 Springview Alley","ShipName":"Legros-Toy"},{"OrderID":"0338-1143","ShipCountry":"BD","ShipAddress":"06 Park Meadow Parkway","ShipName":"Botsford, Kovacek and Hilll"},{"OrderID":"66116-464","ShipCountry":"PH","ShipAddress":"8 Service Terrace","ShipName":"Keebler and Sons"}]},{"RecordID":2,"FirstName":"Nara","LastName":"McAlpine","Company":"Demizz","Email":"nmcalpine1@google.fr","Orders":[{"OrderID":"0591-3213","ShipCountry":"PL","ShipAddress":"7398 7th Point","ShipName":"Koelpin-Larkin"},{"OrderID":"0186-5020","ShipCountry":"ZA","ShipAddress":"7334 Sage Junction","ShipName":"Sanford Group"},]}]');
      $(".m_datatable").mDatatable({
        data: {
          type: "local",
          source: e,
          pageSize: 10,
          saveState: {
            cookie: !0,
            webstorage: !0
          }
        },
        layout: {
          theme: "default",
          scroll: !1,
          height: null,
          footer: !1
        },
        sortable: !0,
        filterable: !1,
        pagination: !0,
        detail: {
          title: "Load sub table",
          content: r
        },
        search: {
          input: $("#generalSearch")
        },
        columns: [{
          field: "RecordID",
          title: "",
          sortable: !1,
          width: 20,
          textAlign: "center"
        }, {
          field: "FirstName",
          title: "First Name"
        }, {
          field: "LastName",
          title: "Last Name"
        }, {
          field: "Company",
          title: "Company"
        }, {
          field: "Email",
          title: "Email"
        }, {
          field: "Actions",
          width: 110,
          title: "Actions",
          sortable: !1,
          overflow: "visible",
          template: function(r) {
            return '\t\t\t\t\t\t<div class="dropdown ' + (r.getDatatable().getPageSize() - r.getIndex() <= 4 ? "dropup" : "") + '">\t\t\t\t\t\t\t<a href="#" class="btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" data-toggle="dropdown">                                <i class="la la-ellipsis-h"></i>                            </a>\t\t\t\t\t\t  \t<div class="dropdown-menu dropdown-menu-right">\t\t\t\t\t\t    \t<a class="dropdown-item" href="#"><i class="la la-edit"></i> Edit Details</a>\t\t\t\t\t\t    \t<a class="dropdown-item" href="#"><i class="la la-leaf"></i> Update Status</a>\t\t\t\t\t\t    \t<a class="dropdown-item" href="#"><i class="la la-print"></i> Generate Report</a>\t\t\t\t\t\t  \t</div>\t\t\t\t\t\t</div>\t\t\t\t\t\t<a href="#" class="m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Edit details">\t\t\t\t\t\t\t<i class="la la-edit"></i>\t\t\t\t\t\t</a>\t\t\t\t\t\t<a href="#" class="m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill" title="Delete">\t\t\t\t\t\t\t<i class="la la-trash"></i>\t\t\t\t\t\t</a>\t\t\t\t\t'
          }
        }]
      })
    };
  return {
    init: function() {
      e()
    }
  }
}();
jQuery(document).ready(function() {
  DatatableChildDataLocalDemo.init()
});
