var ToastrDemo = function () {
    var t = function () {
        function t() {
            return o
        }

        var o, e = -1, n = 0, a = function () {
            var t = ["New order has been placed!", "Are you the six fingered man?", "Inconceivable!", "I do not think that means what you think it means.", "Have fun storming the castle!"];
            return ++e === t.length && (e = 0), t[e]
        }, i = function (t) {
            return t = t || "Clear itself?", t += '<br /><br /><button type="button" class="btn btn-outline-light btn-sm m-btn m-btn--air m-btn--wide clear">Yes</button>'
        };
        $("#showtoast").click(function () {
            var t = $("#toastTypeGroup input:radio:checked").val(), e = $("#message").val(),
                r = $("#title").val() || "", s = $("#showDuration"), l = $("#hideDuration"), c = $("#timeOut"),
                u = $("#extendedTimeOut"), p = $("#showEasing"), d = $("#hideEasing"), h = $("#showMethod"),
                v = $("#hideMethod"), g = n++, f = $("#addClear").prop("checked");
            toastr.options = {
                closeButton: $("#closeButton").prop("checked"),
                debug: $("#debugInfo").prop("checked"),
                newestOnTop: $("#newestOnTop").prop("checked"),
                progressBar: $("#progressBar").prop("checked"),
                positionClass: $("#positionGroup input:radio:checked").val() || "toast-top-right",
                preventDuplicates: $("#preventDuplicates").prop("checked"),
                onclick: null
            }, $("#addBehaviorOnToastClick").prop("checked") && (toastr.options.onclick = function () {
                alert("You can perform some custom action after a toast goes away")
            }), s.val().length && (toastr.options.showDuration = s.val()), l.val().length && (toastr.options.hideDuration = l.val()), c.val().length && (toastr.options.timeOut = f ? 0 : c.val()), u.val().length && (toastr.options.extendedTimeOut = f ? 0 : u.val()), p.val().length && (toastr.options.showEasing = p.val()), d.val().length && (toastr.options.hideEasing = d.val()), h.val().length && (toastr.options.showMethod = h.val()), v.val().length && (toastr.options.hideMethod = v.val()), f && (e = i(e), toastr.options.tapToDismiss = !1), e || (e = a()), $("#toastrOptions").text("toastr.options = " + JSON.stringify(toastr.options, null, 2) + ";\n\ntoastr." + t + '("' + e + (r ? '", "' + r : "") + '");');
            var k = toastr[t](e, r);
            o = k, void 0 !== k && (k.find("#okBtn").length && k.delegate("#okBtn", "click", function () {
                alert("you clicked me. i was toast #" + g + ". goodbye!"), k.remove()
            }), k.find("#surpriseBtn").length && k.delegate("#surpriseBtn", "click", function () {
                alert("Surprise! you clicked me. i was toast #" + g + ". You could perform an action here.")
            }), k.find(".clear").length && k.delegate(".clear", "click", function () {
                toastr.clear(k, {force: !0})
            }))
        }), $("#clearlasttoast").click(function () {
            toastr.clear(t())
        }), $("#cleartoasts").click(function () {
            toastr.clear()
        })
    };
    return {
        init: function () {
            t()
        }
    }
}();
jQuery(document).ready(function () {
    ToastrDemo.init()
});