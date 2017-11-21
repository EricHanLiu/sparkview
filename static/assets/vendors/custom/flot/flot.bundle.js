! function(e) {
  e.color = {}, e.color.make = function(t, i, o, n) {
    var r = {};
    return r.r = t || 0, r.g = i || 0, r.b = o || 0, r.a = null != n ? n : 1, r.add = function(e, t) {
      for (var i = 0; i < e.length; ++i) r[e.charAt(i)] += t;
      return r.normalize()
    }, r.scale = function(e, t) {
      for (var i = 0; i < e.length; ++i) r[e.charAt(i)] *= t;
      return r.normalize()
    }, r.toString = function() {
      return r.a >= 1 ? "rgb(" + [r.r, r.g, r.b].join(",") + ")" : "rgba(" + [r.r, r.g, r.b, r.a].join(",") + ")"
    }, r.normalize = function() {
      function e(e, t, i) {
        return t < e ? e : t > i ? i : t
      }
      return r.r = e(0, parseInt(r.r), 255), r.g = e(0, parseInt(r.g), 255), r.b = e(0, parseInt(r.b), 255), r.a = e(0, r.a, 1), r
    }, r.clone = function() {
      return e.color.make(r.r, r.b, r.g, r.a)
    }, r.normalize()
  }, e.color.extract = function(t, i) {
    var o;
    do {
      if ("" != (o = t.css(i).toLowerCase()) && "transparent" != o) break;
      t = t.parent()
    } while (t.length && !e.nodeName(t.get(0), "body"));
    return "rgba(0, 0, 0, 0)" == o && (o = "transparent"), e.color.parse(o)
  }, e.color.parse = function(i) {
    var o, n = e.color.make;
    if (o = /rgb\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*\)/.exec(i)) return n(parseInt(o[1], 10), parseInt(o[2], 10), parseInt(o[3], 10));
    if (o = /rgba\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]+(?:\.[0-9]+)?)\s*\)/.exec(i)) return n(parseInt(o[1], 10), parseInt(o[2], 10), parseInt(o[3], 10), parseFloat(o[4]));
    if (o = /rgb\(\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*\)/.exec(i)) return n(2.55 * parseFloat(o[1]), 2.55 * parseFloat(o[2]), 2.55 * parseFloat(o[3]));
    if (o = /rgba\(\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\s*\)/.exec(i)) return n(2.55 * parseFloat(o[1]), 2.55 * parseFloat(o[2]), 2.55 * parseFloat(o[3]), parseFloat(o[4]));
    if (o = /#([a-fA-F0-9]{2})([a-fA-F0-9]{2})([a-fA-F0-9]{2})/.exec(i)) return n(parseInt(o[1], 16), parseInt(o[2], 16), parseInt(o[3], 16));
    if (o = /#([a-fA-F0-9])([a-fA-F0-9])([a-fA-F0-9])/.exec(i)) return n(parseInt(o[1] + o[1], 16), parseInt(o[2] + o[2], 16), parseInt(o[3] + o[3], 16));
    var r = e.trim(i).toLowerCase();
    return "transparent" == r ? n(255, 255, 255, 0) : (o = t[r] || [0, 0, 0], n(o[0], o[1], o[2]))
  };
  var t = {
    aqua: [0, 255, 255],
    azure: [240, 255, 255],
    beige: [245, 245, 220],
    black: [0, 0, 0],
    blue: [0, 0, 255],
    brown: [165, 42, 42],
    cyan: [0, 255, 255],
    darkblue: [0, 0, 139],
    darkcyan: [0, 139, 139],
    darkgrey: [169, 169, 169],
    darkgreen: [0, 100, 0],
    darkkhaki: [189, 183, 107],
    darkmagenta: [139, 0, 139],
    darkolivegreen: [85, 107, 47],
    darkorange: [255, 140, 0],
    darkorchid: [153, 50, 204],
    darkred: [139, 0, 0],
    darksalmon: [233, 150, 122],
    darkviolet: [148, 0, 211],
    fuchsia: [255, 0, 255],
    gold: [255, 215, 0],
    green: [0, 128, 0],
    indigo: [75, 0, 130],
    khaki: [240, 230, 140],
    lightblue: [173, 216, 230],
    lightcyan: [224, 255, 255],
    lightgreen: [144, 238, 144],
    lightgrey: [211, 211, 211],
    lightpink: [255, 182, 193],
    lightyellow: [255, 255, 224],
    lime: [0, 255, 0],
    magenta: [255, 0, 255],
    maroon: [128, 0, 0],
    navy: [0, 0, 128],
    olive: [128, 128, 0],
    orange: [255, 165, 0],
    pink: [255, 192, 203],
    purple: [128, 0, 128],
    violet: [128, 0, 128],
    red: [255, 0, 0],
    silver: [192, 192, 192],
    white: [255, 255, 255],
    yellow: [255, 255, 0]
  }
}(jQuery),
function(e) {
  function t(t, i) {
    var o = i.children("." + t)[0];
    if (null == o && (o = document.createElement("canvas"), o.className = t, e(o).css({
        direction: "ltr",
        position: "absolute",
        left: 0,
        top: 0
      }).appendTo(i), !o.getContext)) {
      if (!window.G_vmlCanvasManager) throw new Error("Canvas is not available. If you're using IE with a fall-back such as Excanvas, then there's either a mistake in your conditional include, or the page has no DOCTYPE and is rendering in Quirks Mode.");
      o = window.G_vmlCanvasManager.initElement(o)
    }
    this.element = o;
    var n = this.context = o.getContext("2d"),
      r = window.devicePixelRatio || 1,
      a = n.webkitBackingStorePixelRatio || n.mozBackingStorePixelRatio || n.msBackingStorePixelRatio || n.oBackingStorePixelRatio || n.backingStorePixelRatio || 1;
    this.pixelRatio = r / a, this.resize(i.width(), i.height()), this.textContainer = null, this.text = {}, this._textCache = {}
  }

  function i(i, n, r, a) {
    function l(e, t) {
      t = [ue].concat(t);
      for (var i = 0; i < e.length; ++i) e[i].apply(this, t)
    }

    function s(e) {
      K = c(e), d(), g()
    }

    function c(t) {
      for (var i = [], o = 0; o < t.length; ++o) {
        var n = e.extend(!0, {}, Z.series);
        null != t[o].data ? (n.data = t[o].data, delete t[o].data, e.extend(!0, n, t[o]), t[o].data = n.data) : n.data = t[o], i.push(n)
      }
      return i
    }

    function h(e, t) {
      var i = e[t + "axis"];
      return "object" == typeof i && (i = i.n), "number" != typeof i && (i = 1), i
    }

    function u() {
      return e.grep(re.concat(ae), function(e) {
        return e
      })
    }

    function f(e) {
      var t, i, o = {};
      for (t = 0; t < re.length; ++t)(i = re[t]) && i.used && (o["x" + i.n] = i.c2p(e.left));
      for (t = 0; t < ae.length; ++t)(i = ae[t]) && i.used && (o["y" + i.n] = i.c2p(e.top));
      return void 0 !== o.x1 && (o.x = o.x1), void 0 !== o.y1 && (o.y = o.y1), o
    }

    function p(t, i) {
      return t[i - 1] || (t[i - 1] = {
        n: i,
        direction: t == re ? "x" : "y",
        options: e.extend(!0, {}, t == re ? Z.xaxis : Z.yaxis)
      }), t[i - 1]
    }

    function d() {
      var t, i = K.length,
        o = -1;
      for (t = 0; t < K.length; ++t) {
        var n = K[t].color;
        null != n && (i--, "number" == typeof n && n > o && (o = n))
      }
      i <= o && (i = o + 1);
      var r, a = [],
        l = Z.colors,
        s = l.length,
        c = 0;
      for (t = 0; t < i; t++) r = e.color.parse(l[t % s] || "#666"), t % s == 0 && t && (c = c >= 0 ? c < .5 ? -c - .2 : 0 : -c), a[t] = r.scale("rgb", 1 + c);
      var u, f = 0;
      for (t = 0; t < K.length; ++t) {
        if (null == (u = K[t]).color ? (u.color = a[f].toString(), ++f) : "number" == typeof u.color && (u.color = a[u.color].toString()), null == u.lines.show) {
          var d, g = !0;
          for (d in u)
            if (u[d] && u[d].show) {
              g = !1;
              break
            }
          g && (u.lines.show = !0)
        }
        null == u.lines.zero && (u.lines.zero = !!u.lines.fill), u.xaxis = p(re, h(u, "x")), u.yaxis = p(ae, h(u, "y"))
      }
    }

    function g() {
      function t(e, t, i) {
        t < e.datamin && t != -v && (e.datamin = t), i > e.datamax && i != v && (e.datamax = i)
      }
      var i, o, n, r, a, s, c, h, f, p, d, g, m = Number.POSITIVE_INFINITY,
        x = Number.NEGATIVE_INFINITY,
        v = Number.MAX_VALUE;
      for (e.each(u(), function(e, t) {
          t.datamin = m, t.datamax = x, t.used = !1
        }), i = 0; i < K.length; ++i)(a = K[i]).datapoints = {
        points: []
      }, l(he.processRawData, [a, a.data, a.datapoints]);
      for (i = 0; i < K.length; ++i) {
        if (a = K[i], d = a.data, !(g = a.datapoints.format)) {
          if ((g = []).push({
              x: !0,
              number: !0,
              required: !0
            }), g.push({
              y: !0,
              number: !0,
              required: !0
            }), a.bars.show || a.lines.show && a.lines.fill) {
            var b = !!(a.bars.show && a.bars.zero || a.lines.show && a.lines.zero);
            g.push({
              y: !0,
              number: !0,
              required: !1,
              defaultValue: 0,
              autoscale: b
            }), a.bars.horizontal && (delete g[g.length - 1].y, g[g.length - 1].x = !0)
          }
          a.datapoints.format = g
        }
        if (null == a.datapoints.pointsize) {
          a.datapoints.pointsize = g.length, c = a.datapoints.pointsize, s = a.datapoints.points;
          var k = a.lines.show && a.lines.steps;
          for (a.xaxis.used = a.yaxis.used = !0, o = n = 0; o < d.length; ++o, n += c) {
            var y = null == (p = d[o]);
            if (!y)
              for (r = 0; r < c; ++r) h = p[r], (f = g[r]) && (f.number && null != h && (h = +h, isNaN(h) ? h = null : h == 1 / 0 ? h = v : h == -1 / 0 && (h = -v)), null == h && (f.required && (y = !0), null != f.defaultValue && (h = f.defaultValue))), s[n + r] = h;
            if (y)
              for (r = 0; r < c; ++r) null != (h = s[n + r]) && !1 !== (f = g[r]).autoscale && (f.x && t(a.xaxis, h, h), f.y && t(a.yaxis, h, h)), s[n + r] = null;
            else if (k && n > 0 && null != s[n - c] && s[n - c] != s[n] && s[n - c + 1] != s[n + 1]) {
              for (r = 0; r < c; ++r) s[n + c + r] = s[n + r];
              s[n + 1] = s[n - c + 1], n += c
            }
          }
        }
      }
      for (i = 0; i < K.length; ++i) a = K[i], l(he.processDatapoints, [a, a.datapoints]);
      for (i = 0; i < K.length; ++i) {
        s = (a = K[i]).datapoints.points, c = a.datapoints.pointsize, g = a.datapoints.format;
        var w = m,
          M = m,
          T = x,
          C = x;
        for (o = 0; o < s.length; o += c)
          if (null != s[o])
            for (r = 0; r < c; ++r) h = s[o + r], (f = g[r]) && !1 !== f.autoscale && h != v && h != -v && (f.x && (h < w && (w = h), h > T && (T = h)), f.y && (h < M && (M = h), h > C && (C = h)));
        if (a.bars.show) {
          var A;
          switch (a.bars.align) {
            case "left":
              A = 0;
              break;
            case "right":
              A = -a.bars.barWidth;
              break;
            default:
              A = -a.bars.barWidth / 2
          }
          a.bars.horizontal ? (M += A, C += A + a.bars.barWidth) : (w += A, T += A + a.bars.barWidth)
        }
        t(a.xaxis, w, T), t(a.yaxis, M, C)
      }
      e.each(u(), function(e, t) {
        t.datamin == m && (t.datamin = null), t.datamax == x && (t.datamax = null)
      })
    }

    function m() {
      pe && clearTimeout(pe), ie.unbind("mousemove", E), ie.unbind("mouseleave", H), ie.unbind("click", B), l(he.shutdown, [ie])
    }

    function x(e) {
      function t(e) {
        return e
      }
      var i, o, n = e.options.transform || t,
        r = e.options.inverseTransform;
      "x" == e.direction ? (i = e.scale = se / Math.abs(n(e.max) - n(e.min)), o = Math.min(n(e.max), n(e.min))) : (i = e.scale = ce / Math.abs(n(e.max) - n(e.min)), i = -i, o = Math.max(n(e.max), n(e.min))), e.p2c = n == t ? function(e) {
        return (e - o) * i
      } : function(e) {
        return (n(e) - o) * i
      }, e.c2p = r ? function(e) {
        return r(o + e / i)
      } : function(e) {
        return o + e / i
      }
    }

    function v(e) {
      for (var t = e.options, i = e.ticks || [], o = t.labelWidth || 0, n = t.labelHeight || 0, r = o || ("x" == e.direction ? Math.floor(ee.width / (i.length || 1)) : null), a = e.direction + "Axis " + e.direction + e.n + "Axis", l = "flot-" + e.direction + "-axis flot-" + e.direction + e.n + "-axis " + a, s = t.font || "flot-tick-label tickLabel", c = 0; c < i.length; ++c) {
        var h = i[c];
        if (h.label) {
          var u = ee.getTextInfo(l, h.label, s, null, r);
          o = Math.max(o, u.width), n = Math.max(n, u.height)
        }
      }
      e.labelWidth = t.labelWidth || o, e.labelHeight = t.labelHeight || n
    }

    function b(t) {
      var i = t.labelWidth,
        o = t.labelHeight,
        n = t.options.position,
        r = "x" === t.direction,
        a = t.options.tickLength,
        l = Z.grid.axisMargin,
        s = Z.grid.labelMargin,
        c = !0,
        h = !0,
        u = !0,
        f = !1;
      e.each(r ? re : ae, function(e, i) {
        i && (i.show || i.reserveSpace) && (i === t ? f = !0 : i.options.position === n && (f ? h = !1 : c = !1), f || (u = !1))
      }), h && (l = 0), null == a && (a = u ? "full" : 5), isNaN(+a) || (s += +a), r ? (o += s, "bottom" == n ? (le.bottom += o + l, t.box = {
        top: ee.height - le.bottom,
        height: o
      }) : (t.box = {
        top: le.top + l,
        height: o
      }, le.top += o + l)) : (i += s, "left" == n ? (t.box = {
        left: le.left + l,
        width: i
      }, le.left += i + l) : (le.right += i + l, t.box = {
        left: ee.width - le.right,
        width: i
      })), t.position = n, t.tickLength = a, t.box.padding = s, t.innermost = c
    }

    function k(e) {
      "x" == e.direction ? (e.box.left = le.left - e.labelWidth / 2, e.box.width = ee.width - le.left - le.right + e.labelWidth) : (e.box.top = le.top - e.labelHeight / 2, e.box.height = ee.height - le.bottom - le.top + e.labelHeight)
    }

    function y() {
      var t, i = Z.grid.minBorderMargin;
      if (null == i)
        for (i = 0, t = 0; t < K.length; ++t) i = Math.max(i, 2 * (K[t].points.radius + K[t].points.lineWidth / 2));
      var o = {
        left: i,
        right: i,
        top: i,
        bottom: i
      };
      e.each(u(), function(e, t) {
        t.reserveSpace && t.ticks && t.ticks.length && ("x" === t.direction ? (o.left = Math.max(o.left, t.labelWidth / 2), o.right = Math.max(o.right, t.labelWidth / 2)) : (o.bottom = Math.max(o.bottom, t.labelHeight / 2), o.top = Math.max(o.top, t.labelHeight / 2)))
      }), le.left = Math.ceil(Math.max(o.left, le.left)), le.right = Math.ceil(Math.max(o.right, le.right)), le.top = Math.ceil(Math.max(o.top, le.top)), le.bottom = Math.ceil(Math.max(o.bottom, le.bottom))
    }

    function w() {
      var t, i = u(),
        o = Z.grid.show;
      for (var n in le) {
        var r = Z.grid.margin || 0;
        le[n] = "number" == typeof r ? r : r[n] || 0
      }
      l(he.processOffset, [le]);
      for (var n in le) "object" == typeof Z.grid.borderWidth ? le[n] += o ? Z.grid.borderWidth[n] : 0 : le[n] += o ? Z.grid.borderWidth : 0;
      if (e.each(i, function(e, t) {
          var i = t.options;
          t.show = null == i.show ? t.used : i.show, t.reserveSpace = null == i.reserveSpace ? t.show : i.reserveSpace, M(t)
        }), o) {
        var a = e.grep(i, function(e) {
          return e.show || e.reserveSpace
        });
        for (e.each(a, function(e, t) {
            T(t), C(t), A(t, t.ticks), v(t)
          }), t = a.length - 1; t >= 0; --t) b(a[t]);
        y(), e.each(a, function(e, t) {
          k(t)
        })
      }
      se = ee.width - le.left - le.right, ce = ee.height - le.bottom - le.top, e.each(i, function(e, t) {
        x(t)
      }), o && P(), j()
    }

    function M(e) {
      var t = e.options,
        i = +(null != t.min ? t.min : e.datamin),
        o = +(null != t.max ? t.max : e.datamax),
        n = o - i;
      if (0 == n) {
        var r = 0 == o ? 1 : .01;
        null == t.min && (i -= r), null != t.max && null == t.min || (o += r)
      } else {
        var a = t.autoscaleMargin;
        null != a && (null == t.min && (i -= n * a) < 0 && null != e.datamin && e.datamin >= 0 && (i = 0), null == t.max && (o += n * a) > 0 && null != e.datamax && e.datamax <= 0 && (o = 0))
      }
      e.min = i, e.max = o
    }

    function T(t) {
      var i, n = t.options;
      i = "number" == typeof n.ticks && n.ticks > 0 ? n.ticks : .3 * Math.sqrt("x" == t.direction ? ee.width : ee.height);
      var r = (t.max - t.min) / i,
        a = -Math.floor(Math.log(r) / Math.LN10),
        l = n.tickDecimals;
      null != l && a > l && (a = l);
      var s, c = Math.pow(10, -a),
        h = r / c;
      if (h < 1.5 ? s = 1 : h < 3 ? (s = 2, h > 2.25 && (null == l || a + 1 <= l) && (s = 2.5, ++a)) : s = h < 7.5 ? 5 : 10, s *= c, null != n.minTickSize && s < n.minTickSize && (s = n.minTickSize), t.delta = r, t.tickDecimals = Math.max(0, null != l ? l : a), t.tickSize = n.tickSize || s, "time" == n.mode && !t.tickGenerator) throw new Error("Time mode requires the flot.time plugin.");
      if (t.tickGenerator || (t.tickGenerator = function(e) {
          var t, i = [],
            n = o(e.min, e.tickSize),
            r = 0,
            a = Number.NaN;
          do {
            t = a, a = n + r * e.tickSize, i.push(a), ++r
          } while (a < e.max && a != t);
          return i
        }, t.tickFormatter = function(e, t) {
          var i = t.tickDecimals ? Math.pow(10, t.tickDecimals) : 1,
            o = "" + Math.round(e * i) / i;
          if (null != t.tickDecimals) {
            var n = o.indexOf("."),
              r = -1 == n ? 0 : o.length - n - 1;
            if (r < t.tickDecimals) return (r ? o : o + ".") + ("" + i).substr(1, t.tickDecimals - r)
          }
          return o
        }), e.isFunction(n.tickFormatter) && (t.tickFormatter = function(e, t) {
          return "" + n.tickFormatter(e, t)
        }), null != n.alignTicksWithAxis) {
        var u = ("x" == t.direction ? re : ae)[n.alignTicksWithAxis - 1];
        if (u && u.used && u != t) {
          var f = t.tickGenerator(t);
          if (f.length > 0 && (null == n.min && (t.min = Math.min(t.min, f[0])), null == n.max && f.length > 1 && (t.max = Math.max(t.max, f[f.length - 1]))), t.tickGenerator = function(e) {
              var t, i, o = [];
              for (i = 0; i < u.ticks.length; ++i) t = (u.ticks[i].v - u.min) / (u.max - u.min), t = e.min + t * (e.max - e.min), o.push(t);
              return o
            }, !t.mode && null == n.tickDecimals) {
            var p = Math.max(0, 1 - Math.floor(Math.log(t.delta) / Math.LN10)),
              d = t.tickGenerator(t);
            d.length > 1 && /\..*0$/.test((d[1] - d[0]).toFixed(p)) || (t.tickDecimals = p)
          }
        }
      }
    }

    function C(t) {
      var i = t.options.ticks,
        o = [];
      null == i || "number" == typeof i && i > 0 ? o = t.tickGenerator(t) : i && (o = e.isFunction(i) ? i(t) : i);
      var n, r;
      for (t.ticks = [], n = 0; n < o.length; ++n) {
        var a = null,
          l = o[n];
        "object" == typeof l ? (r = +l[0], l.length > 1 && (a = l[1])) : r = +l, null == a && (a = t.tickFormatter(r, t)), isNaN(r) || t.ticks.push({
          v: r,
          label: a
        })
      }
    }

    function A(e, t) {
      e.options.autoscaleMargin && t.length > 0 && (null == e.options.min && (e.min = Math.min(e.min, t[0].v)), null == e.options.max && t.length > 1 && (e.max = Math.max(e.max, t[t.length - 1].v)))
    }

    function z() {
      ee.clear(), l(he.drawBackground, [oe]);
      var e = Z.grid;
      e.show && e.backgroundColor && W(), e.show && !e.aboveData && I();
      for (var t = 0; t < K.length; ++t) l(he.drawSeries, [oe, K[t]]), F(K[t]);
      l(he.draw, [oe]), e.show && e.aboveData && I(), ee.render(), X()
    }

    function S(e, t) {
      for (var i, o, n, r, a = u(), l = 0; l < a.length; ++l)
        if ((i = a[l]).direction == t && (r = t + i.n + "axis", e[r] || 1 != i.n || (r = t + "axis"), e[r])) {
          o = e[r].from, n = e[r].to;
          break
        }
      if (e[r] || (i = "x" == t ? re[0] : ae[0], o = e[t + "1"], n = e[t + "2"]), null != o && null != n && o > n) {
        var s = o;
        o = n, n = s
      }
      return {
        from: o,
        to: n,
        axis: i
      }
    }

    function W() {
      oe.save(), oe.translate(le.left, le.top), oe.fillStyle = $(Z.grid.backgroundColor, ce, 0, "rgba(255, 255, 255, 0)"), oe.fillRect(0, 0, se, ce), oe.restore()
    }

    function I() {
      var t, i, o, n;
      oe.save(), oe.translate(le.left, le.top);
      var r = Z.grid.markings;
      if (r)
        for (e.isFunction(r) && ((i = ue.getAxes()).xmin = i.xaxis.min, i.xmax = i.xaxis.max, i.ymin = i.yaxis.min, i.ymax = i.yaxis.max, r = r(i)), t = 0; t < r.length; ++t) {
          var a = r[t],
            l = S(a, "x"),
            s = S(a, "y");
          if (null == l.from && (l.from = l.axis.min), null == l.to && (l.to = l.axis.max), null == s.from && (s.from = s.axis.min), null == s.to && (s.to = s.axis.max), !(l.to < l.axis.min || l.from > l.axis.max || s.to < s.axis.min || s.from > s.axis.max)) {
            l.from = Math.max(l.from, l.axis.min), l.to = Math.min(l.to, l.axis.max), s.from = Math.max(s.from, s.axis.min), s.to = Math.min(s.to, s.axis.max);
            var c = l.from === l.to,
              h = s.from === s.to;
            if (!c || !h)
              if (l.from = Math.floor(l.axis.p2c(l.from)), l.to = Math.floor(l.axis.p2c(l.to)), s.from = Math.floor(s.axis.p2c(s.from)), s.to = Math.floor(s.axis.p2c(s.to)), c || h) {
                var f = a.lineWidth || Z.grid.markingsLineWidth,
                  p = f % 2 ? .5 : 0;
                oe.beginPath(), oe.strokeStyle = a.color || Z.grid.markingsColor, oe.lineWidth = f, c ? (oe.moveTo(l.to + p, s.from), oe.lineTo(l.to + p, s.to)) : (oe.moveTo(l.from, s.to + p), oe.lineTo(l.to, s.to + p)), oe.stroke()
              } else oe.fillStyle = a.color || Z.grid.markingsColor, oe.fillRect(l.from, s.to, l.to - l.from, s.from - s.to)
          }
        }
      i = u(), o = Z.grid.borderWidth;
      for (var d = 0; d < i.length; ++d) {
        var g, m, x, v, b = i[d],
          k = b.box,
          y = b.tickLength;
        if (b.show && 0 != b.ticks.length) {
          for (oe.lineWidth = 1, "x" == b.direction ? (g = 0, m = "full" == y ? "top" == b.position ? 0 : ce : k.top - le.top + ("top" == b.position ? k.height : 0)) : (m = 0, g = "full" == y ? "left" == b.position ? 0 : se : k.left - le.left + ("left" == b.position ? k.width : 0)), b.innermost || (oe.strokeStyle = b.options.color, oe.beginPath(), x = v = 0, "x" == b.direction ? x = se + 1 : v = ce + 1, 1 == oe.lineWidth && ("x" == b.direction ? m = Math.floor(m) + .5 : g = Math.floor(g) + .5), oe.moveTo(g, m), oe.lineTo(g + x, m + v), oe.stroke()), oe.strokeStyle = b.options.tickColor, oe.beginPath(), t = 0; t < b.ticks.length; ++t) {
            var w = b.ticks[t].v;
            x = v = 0, isNaN(w) || w < b.min || w > b.max || "full" == y && ("object" == typeof o && o[b.position] > 0 || o > 0) && (w == b.min || w == b.max) || ("x" == b.direction ? (g = b.p2c(w), v = "full" == y ? -ce : y, "top" == b.position && (v = -v)) : (m = b.p2c(w), x = "full" == y ? -se : y, "left" == b.position && (x = -x)), 1 == oe.lineWidth && ("x" == b.direction ? g = Math.floor(g) + .5 : m = Math.floor(m) + .5), oe.moveTo(g, m), oe.lineTo(g + x, m + v))
          }
          oe.stroke()
        }
      }
      o && (n = Z.grid.borderColor, "object" == typeof o || "object" == typeof n ? ("object" != typeof o && (o = {
        top: o,
        right: o,
        bottom: o,
        left: o
      }), "object" != typeof n && (n = {
        top: n,
        right: n,
        bottom: n,
        left: n
      }), o.top > 0 && (oe.strokeStyle = n.top, oe.lineWidth = o.top, oe.beginPath(), oe.moveTo(0 - o.left, 0 - o.top / 2), oe.lineTo(se, 0 - o.top / 2), oe.stroke()), o.right > 0 && (oe.strokeStyle = n.right, oe.lineWidth = o.right, oe.beginPath(), oe.moveTo(se + o.right / 2, 0 - o.top), oe.lineTo(se + o.right / 2, ce), oe.stroke()), o.bottom > 0 && (oe.strokeStyle = n.bottom, oe.lineWidth = o.bottom, oe.beginPath(), oe.moveTo(se + o.right, ce + o.bottom / 2), oe.lineTo(0, ce + o.bottom / 2), oe.stroke()), o.left > 0 && (oe.strokeStyle = n.left, oe.lineWidth = o.left, oe.beginPath(), oe.moveTo(0 - o.left / 2, ce + o.bottom), oe.lineTo(0 - o.left / 2, 0), oe.stroke())) : (oe.lineWidth = o, oe.strokeStyle = Z.grid.borderColor, oe.strokeRect(-o / 2, -o / 2, se + o, ce + o))), oe.restore()
    }

    function P() {
      e.each(u(), function(e, t) {
        var i, o, n, r, a, l = t.box,
          s = t.direction + "Axis " + t.direction + t.n + "Axis",
          c = "flot-" + t.direction + "-axis flot-" + t.direction + t.n + "-axis " + s,
          h = t.options.font || "flot-tick-label tickLabel";
        if (ee.removeText(c), t.show && 0 != t.ticks.length)
          for (var u = 0; u < t.ticks.length; ++u) !(i = t.ticks[u]).label || i.v < t.min || i.v > t.max || ("x" == t.direction ? (r = "center", o = le.left + t.p2c(i.v), "bottom" == t.position ? n = l.top + l.padding : (n = l.top + l.height - l.padding, a = "bottom")) : (a = "middle", n = le.top + t.p2c(i.v), "left" == t.position ? (o = l.left + l.width - l.padding, r = "right") : o = l.left + l.padding), ee.addText(c, o, n, i.label, h, null, null, r, a))
      })
    }

    function F(e) {
      e.lines.show && O(e), e.bars.show && D(e), e.points.show && R(e)
    }

    function O(e) {
      function t(e, t, i, o, n) {
        var r = e.points,
          a = e.pointsize,
          l = null,
          s = null;
        oe.beginPath();
        for (var c = a; c < r.length; c += a) {
          var h = r[c - a],
            u = r[c - a + 1],
            f = r[c],
            p = r[c + 1];
          if (null != h && null != f) {
            if (u <= p && u < n.min) {
              if (p < n.min) continue;
              h = (n.min - u) / (p - u) * (f - h) + h, u = n.min
            } else if (p <= u && p < n.min) {
              if (u < n.min) continue;
              f = (n.min - u) / (p - u) * (f - h) + h, p = n.min
            }
            if (u >= p && u > n.max) {
              if (p > n.max) continue;
              h = (n.max - u) / (p - u) * (f - h) + h, u = n.max
            } else if (p >= u && p > n.max) {
              if (u > n.max) continue;
              f = (n.max - u) / (p - u) * (f - h) + h, p = n.max
            }
            if (h <= f && h < o.min) {
              if (f < o.min) continue;
              u = (o.min - h) / (f - h) * (p - u) + u, h = o.min
            } else if (f <= h && f < o.min) {
              if (h < o.min) continue;
              p = (o.min - h) / (f - h) * (p - u) + u, f = o.min
            }
            if (h >= f && h > o.max) {
              if (f > o.max) continue;
              u = (o.max - h) / (f - h) * (p - u) + u, h = o.max
            } else if (f >= h && f > o.max) {
              if (h > o.max) continue;
              p = (o.max - h) / (f - h) * (p - u) + u, f = o.max
            }
            h == l && u == s || oe.moveTo(o.p2c(h) + t, n.p2c(u) + i), l = f, s = p, oe.lineTo(o.p2c(f) + t, n.p2c(p) + i)
          }
        }
        oe.stroke()
      }
      oe.save(), oe.translate(le.left, le.top), oe.lineJoin = "round";
      var i = e.lines.lineWidth,
        o = e.shadowSize;
      if (i > 0 && o > 0) {
        oe.lineWidth = o, oe.strokeStyle = "rgba(0,0,0,0.1)";
        var n = Math.PI / 18;
        t(e.datapoints, Math.sin(n) * (i / 2 + o / 2), Math.cos(n) * (i / 2 + o / 2), e.xaxis, e.yaxis), oe.lineWidth = o / 2, t(e.datapoints, Math.sin(n) * (i / 2 + o / 4), Math.cos(n) * (i / 2 + o / 4), e.xaxis, e.yaxis)
      }
      oe.lineWidth = i, oe.strokeStyle = e.color;
      var r = L(e.lines, e.color, 0, ce);
      r && (oe.fillStyle = r, function(e, t, i) {
        for (var o = e.points, n = e.pointsize, r = Math.min(Math.max(0, i.min), i.max), a = 0, l = !1, s = 1, c = 0, h = 0; !(n > 0 && a > o.length + n);) {
          var u = o[(a += n) - n],
            f = o[a - n + s],
            p = o[a],
            d = o[a + s];
          if (l) {
            if (n > 0 && null != u && null == p) {
              h = a, n = -n, s = 2;
              continue
            }
            if (n < 0 && a == c + n) {
              oe.fill(), l = !1, s = 1, a = c = h + (n = -n);
              continue
            }
          }
          if (null != u && null != p) {
            if (u <= p && u < t.min) {
              if (p < t.min) continue;
              f = (t.min - u) / (p - u) * (d - f) + f, u = t.min
            } else if (p <= u && p < t.min) {
              if (u < t.min) continue;
              d = (t.min - u) / (p - u) * (d - f) + f, p = t.min
            }
            if (u >= p && u > t.max) {
              if (p > t.max) continue;
              f = (t.max - u) / (p - u) * (d - f) + f, u = t.max
            } else if (p >= u && p > t.max) {
              if (u > t.max) continue;
              d = (t.max - u) / (p - u) * (d - f) + f, p = t.max
            }
            if (l || (oe.beginPath(), oe.moveTo(t.p2c(u), i.p2c(r)), l = !0), f >= i.max && d >= i.max) oe.lineTo(t.p2c(u), i.p2c(i.max)), oe.lineTo(t.p2c(p), i.p2c(i.max));
            else if (f <= i.min && d <= i.min) oe.lineTo(t.p2c(u), i.p2c(i.min)), oe.lineTo(t.p2c(p), i.p2c(i.min));
            else {
              var g = u,
                m = p;
              f <= d && f < i.min && d >= i.min ? (u = (i.min - f) / (d - f) * (p - u) + u, f = i.min) : d <= f && d < i.min && f >= i.min && (p = (i.min - f) / (d - f) * (p - u) + u, d = i.min), f >= d && f > i.max && d <= i.max ? (u = (i.max - f) / (d - f) * (p - u) + u, f = i.max) : d >= f && d > i.max && f <= i.max && (p = (i.max - f) / (d - f) * (p - u) + u, d = i.max), u != g && oe.lineTo(t.p2c(g), i.p2c(f)), oe.lineTo(t.p2c(u), i.p2c(f)), oe.lineTo(t.p2c(p), i.p2c(d)), p != m && (oe.lineTo(t.p2c(p), i.p2c(d)), oe.lineTo(t.p2c(m), i.p2c(d)))
            }
          }
        }
      }(e.datapoints, e.xaxis, e.yaxis)), i > 0 && t(e.datapoints, 0, 0, e.xaxis, e.yaxis), oe.restore()
    }

    function R(e) {
      function t(e, t, i, o, n, r, a, l) {
        for (var s = e.points, c = e.pointsize, h = 0; h < s.length; h += c) {
          var u = s[h],
            f = s[h + 1];
          null == u || u < r.min || u > r.max || f < a.min || f > a.max || (oe.beginPath(), u = r.p2c(u), f = a.p2c(f) + o, "circle" == l ? oe.arc(u, f, t, 0, n ? Math.PI : 2 * Math.PI, !1) : l(oe, u, f, t, n), oe.closePath(), i && (oe.fillStyle = i, oe.fill()), oe.stroke())
        }
      }
      oe.save(), oe.translate(le.left, le.top);
      var i = e.points.lineWidth,
        o = e.shadowSize,
        n = e.points.radius,
        r = e.points.symbol;
      if (0 == i && (i = 1e-4), i > 0 && o > 0) {
        var a = o / 2;
        oe.lineWidth = a, oe.strokeStyle = "rgba(0,0,0,0.1)", t(e.datapoints, n, null, a + a / 2, !0, e.xaxis, e.yaxis, r), oe.strokeStyle = "rgba(0,0,0,0.2)", t(e.datapoints, n, null, a / 2, !0, e.xaxis, e.yaxis, r)
      }
      oe.lineWidth = i, oe.strokeStyle = e.color, t(e.datapoints, n, L(e.points, e.color), 0, !1, e.xaxis, e.yaxis, r), oe.restore()
    }

    function N(e, t, i, o, n, r, a, l, s, c, h) {
      var u, f, p, d, g, m, x, v, b;
      c ? (v = m = x = !0, g = !1, d = t + o, p = t + n, (f = e) < (u = i) && (b = f, f = u, u = b, g = !0, m = !1)) : (g = m = x = !0, v = !1, u = e + o, f = e + n, (d = t) < (p = i) && (b = d, d = p, p = b, v = !0, x = !1)), f < a.min || u > a.max || d < l.min || p > l.max || (u < a.min && (u = a.min, g = !1), f > a.max && (f = a.max, m = !1), p < l.min && (p = l.min, v = !1), d > l.max && (d = l.max, x = !1), u = a.p2c(u), p = l.p2c(p), f = a.p2c(f), d = l.p2c(d), r && (s.fillStyle = r(p, d), s.fillRect(u, d, f - u, p - d)), h > 0 && (g || m || x || v) && (s.beginPath(), s.moveTo(u, p), g ? s.lineTo(u, d) : s.moveTo(u, d), x ? s.lineTo(f, d) : s.moveTo(f, d), m ? s.lineTo(f, p) : s.moveTo(f, p), v ? s.lineTo(u, p) : s.moveTo(u, p), s.stroke()))
    }

    function D(e) {
      oe.save(), oe.translate(le.left, le.top), oe.lineWidth = e.bars.lineWidth, oe.strokeStyle = e.color;
      var t;
      switch (e.bars.align) {
        case "left":
          t = 0;
          break;
        case "right":
          t = -e.bars.barWidth;
          break;
        default:
          t = -e.bars.barWidth / 2
      }
      var i = e.bars.fill ? function(t, i) {
        return L(e.bars, e.color, t, i)
      } : null;
      ! function(t, i, o, n, r, a) {
        for (var l = t.points, s = t.pointsize, c = 0; c < l.length; c += s) null != l[c] && N(l[c], l[c + 1], l[c + 2], i, o, n, r, a, oe, e.bars.horizontal, e.bars.lineWidth)
      }(e.datapoints, t, t + e.bars.barWidth, i, e.xaxis, e.yaxis), oe.restore()
    }

    function L(t, i, o, n) {
      var r = t.fill;
      if (!r) return null;
      if (t.fillColor) return $(t.fillColor, o, n, i);
      var a = e.color.parse(i);
      return a.a = "number" == typeof r ? r : .4, a.normalize(), a.toString()
    }

    function j() {
      if (null != Z.legend.container ? e(Z.legend.container).html("") : i.find(".legend").remove(), Z.legend.show) {
        for (var t, o, n = [], r = [], a = !1, l = Z.legend.labelFormatter, s = 0; s < K.length; ++s)(t = K[s]).label && (o = l ? l(t.label, t) : t.label) && r.push({
          label: o,
          color: t.color
        });
        if (Z.legend.sorted)
          if (e.isFunction(Z.legend.sorted)) r.sort(Z.legend.sorted);
          else if ("reverse" == Z.legend.sorted) r.reverse();
        else {
          var c = "descending" != Z.legend.sorted;
          r.sort(function(e, t) {
            return e.label == t.label ? 0 : e.label < t.label != c ? 1 : -1
          })
        }
        for (s = 0; s < r.length; ++s) {
          var h = r[s];
          s % Z.legend.noColumns == 0 && (a && n.push("</tr>"), n.push("<tr>"), a = !0), n.push('<td class="legendColorBox"><div style="border:1px solid ' + Z.legend.labelBoxBorderColor + ';padding:1px"><div style="width:4px;height:0;border:5px solid ' + h.color + ';overflow:hidden"></div></div></td><td class="legendLabel">' + h.label + "</td>")
        }
        if (a && n.push("</tr>"), 0 != n.length) {
          var u = '<table style="font-size:smaller;color:' + Z.grid.color + '">' + n.join("") + "</table>";
          if (null != Z.legend.container) e(Z.legend.container).html(u);
          else {
            var f = "",
              p = Z.legend.position,
              d = Z.legend.margin;
            null == d[0] && (d = [d, d]), "n" == p.charAt(0) ? f += "top:" + (d[1] + le.top) + "px;" : "s" == p.charAt(0) && (f += "bottom:" + (d[1] + le.bottom) + "px;"), "e" == p.charAt(1) ? f += "right:" + (d[0] + le.right) + "px;" : "w" == p.charAt(1) && (f += "left:" + (d[0] + le.left) + "px;");
            var g = e('<div class="legend">' + u.replace('style="', 'style="position:absolute;' + f + ";") + "</div>").appendTo(i);
            if (0 != Z.legend.backgroundOpacity) {
              var m = Z.legend.backgroundColor;
              null == m && ((m = (m = Z.grid.backgroundColor) && "string" == typeof m ? e.color.parse(m) : e.color.extract(g, "background-color")).a = 1, m = m.toString());
              var x = g.children();
              e('<div style="position:absolute;width:' + x.width() + "px;height:" + x.height() + "px;" + f + "background-color:" + m + ';"> </div>').prependTo(g).css("opacity", Z.legend.backgroundOpacity)
            }
          }
        }
      }
    }

    function q(e, t, i) {
      var o, n, r, a = Z.grid.mouseActiveRadius,
        l = a * a + 1,
        s = null;
      for (o = K.length - 1; o >= 0; --o)
        if (i(K[o])) {
          var c = K[o],
            h = c.xaxis,
            u = c.yaxis,
            f = c.datapoints.points,
            p = h.c2p(e),
            d = u.c2p(t),
            g = a / h.scale,
            m = a / u.scale;
          if (r = c.datapoints.pointsize, h.options.inverseTransform && (g = Number.MAX_VALUE), u.options.inverseTransform && (m = Number.MAX_VALUE), c.lines.show || c.points.show)
            for (n = 0; n < f.length; n += r) {
              var x = f[n],
                v = f[n + 1];
              if (null != x && !(x - p > g || x - p < -g || v - d > m || v - d < -m)) {
                var b = Math.abs(h.p2c(x) - e),
                  k = Math.abs(u.p2c(v) - t),
                  y = b * b + k * k;
                y < l && (l = y, s = [o, n / r])
              }
            }
          if (c.bars.show && !s) {
            var w, M;
            switch (c.bars.align) {
              case "left":
                w = 0;
                break;
              case "right":
                w = -c.bars.barWidth;
                break;
              default:
                w = -c.bars.barWidth / 2
            }
            for (M = w + c.bars.barWidth, n = 0; n < f.length; n += r) {
              var x = f[n],
                v = f[n + 1],
                T = f[n + 2];
              null != x && ((K[o].bars.horizontal ? p <= Math.max(T, x) && p >= Math.min(T, x) && d >= v + w && d <= v + M : p >= x + w && p <= x + M && d >= Math.min(T, v) && d <= Math.max(T, v)) && (s = [o, n / r]))
            }
          }
        }
      return s ? (o = s[0], n = s[1], r = K[o].datapoints.pointsize, {
        datapoint: K[o].datapoints.points.slice(n * r, (n + 1) * r),
        dataIndex: n,
        series: K[o],
        seriesIndex: o
      }) : null
    }

    function E(e) {
      Z.grid.hoverable && G("plothover", e, function(e) {
        return 0 != e.hoverable
      })
    }

    function H(e) {
      Z.grid.hoverable && G("plothover", e, function(e) {
        return !1
      })
    }

    function B(e) {
      G("plotclick", e, function(e) {
        return 0 != e.clickable
      })
    }

    function G(e, t, o) {
      var n = ie.offset(),
        r = t.pageX - n.left - le.left,
        a = t.pageY - n.top - le.top,
        l = f({
          left: r,
          top: a
        });
      l.pageX = t.pageX, l.pageY = t.pageY;
      var s = q(r, a, o);
      if (s && (s.pageX = parseInt(s.series.xaxis.p2c(s.datapoint[0]) + n.left + le.left, 10), s.pageY = parseInt(s.series.yaxis.p2c(s.datapoint[1]) + n.top + le.top, 10)), Z.grid.autoHighlight) {
        for (var c = 0; c < fe.length; ++c) {
          var h = fe[c];
          h.auto != e || s && h.series == s.series && h.point[0] == s.datapoint[0] && h.point[1] == s.datapoint[1] || Q(h.series, h.point)
        }
        s && _(s.series, s.datapoint, e)
      }
      i.trigger(e, [l, s])
    }

    function X() {
      var e = Z.interaction.redrawOverlayInterval; - 1 != e ? pe || (pe = setTimeout(Y, e)) : Y()
    }

    function Y() {
      pe = null, ne.save(), te.clear(), ne.translate(le.left, le.top);
      var e, t;
      for (e = 0; e < fe.length; ++e)(t = fe[e]).series.bars.show ? U(t.series, t.point) : J(t.series, t.point);
      ne.restore(), l(he.drawOverlay, [ne])
    }

    function _(e, t, i) {
      if ("number" == typeof e && (e = K[e]), "number" == typeof t) {
        var o = e.datapoints.pointsize;
        t = e.datapoints.points.slice(o * t, o * (t + 1))
      }
      var n = V(e, t); - 1 == n ? (fe.push({
        series: e,
        point: t,
        auto: i
      }), X()) : i || (fe[n].auto = !1)
    }

    function Q(e, t) {
      if (null == e && null == t) return fe = [], void X();
      if ("number" == typeof e && (e = K[e]), "number" == typeof t) {
        var i = e.datapoints.pointsize;
        t = e.datapoints.points.slice(i * t, i * (t + 1))
      }
      var o = V(e, t); - 1 != o && (fe.splice(o, 1), X())
    }

    function V(e, t) {
      for (var i = 0; i < fe.length; ++i) {
        var o = fe[i];
        if (o.series == e && o.point[0] == t[0] && o.point[1] == t[1]) return i
      }
      return -1
    }

    function J(t, i) {
      var o = i[0],
        n = i[1],
        r = t.xaxis,
        a = t.yaxis,
        l = "string" == typeof t.highlightColor ? t.highlightColor : e.color.parse(t.color).scale("a", .5).toString();
      if (!(o < r.min || o > r.max || n < a.min || n > a.max)) {
        var s = t.points.radius + t.points.lineWidth / 2;
        ne.lineWidth = s, ne.strokeStyle = l;
        var c = 1.5 * s;
        o = r.p2c(o), n = a.p2c(n), ne.beginPath(), "circle" == t.points.symbol ? ne.arc(o, n, c, 0, 2 * Math.PI, !1) : t.points.symbol(ne, o, n, c, !1), ne.closePath(), ne.stroke()
      }
    }

    function U(t, i) {
      var o, n = "string" == typeof t.highlightColor ? t.highlightColor : e.color.parse(t.color).scale("a", .5).toString(),
        r = n;
      switch (t.bars.align) {
        case "left":
          o = 0;
          break;
        case "right":
          o = -t.bars.barWidth;
          break;
        default:
          o = -t.bars.barWidth / 2
      }
      ne.lineWidth = t.bars.lineWidth, ne.strokeStyle = n, N(i[0], i[1], i[2] || 0, o, o + t.bars.barWidth, function() {
        return r
      }, t.xaxis, t.yaxis, ne, t.bars.horizontal, t.bars.lineWidth)
    }

    function $(t, i, o, n) {
      if ("string" == typeof t) return t;
      for (var r = oe.createLinearGradient(0, o, 0, i), a = 0, l = t.colors.length; a < l; ++a) {
        var s = t.colors[a];
        if ("string" != typeof s) {
          var c = e.color.parse(n);
          null != s.brightness && (c = c.scale("rgb", s.brightness)), null != s.opacity && (c.a *= s.opacity), s = c.toString()
        }
        r.addColorStop(a / (l - 1), s)
      }
      return r
    }
    var K = [],
      Z = {
        colors: ["#edc240", "#afd8f8", "#cb4b4b", "#4da74d", "#9440ed"],
        legend: {
          show: !0,
          noColumns: 1,
          labelFormatter: null,
          labelBoxBorderColor: "#ccc",
          container: null,
          position: "ne",
          margin: 5,
          backgroundColor: null,
          backgroundOpacity: .85,
          sorted: null
        },
        xaxis: {
          show: null,
          position: "bottom",
          mode: null,
          font: null,
          color: null,
          tickColor: null,
          transform: null,
          inverseTransform: null,
          min: null,
          max: null,
          autoscaleMargin: null,
          ticks: null,
          tickFormatter: null,
          labelWidth: null,
          labelHeight: null,
          reserveSpace: null,
          tickLength: null,
          alignTicksWithAxis: null,
          tickDecimals: null,
          tickSize: null,
          minTickSize: null
        },
        yaxis: {
          autoscaleMargin: .02,
          position: "left"
        },
        xaxes: [],
        yaxes: [],
        series: {
          points: {
            show: !1,
            radius: 3,
            lineWidth: 2,
            fill: !0,
            fillColor: "#ffffff",
            symbol: "circle"
          },
          lines: {
            lineWidth: 2,
            fill: !1,
            fillColor: null,
            steps: !1
          },
          bars: {
            show: !1,
            lineWidth: 2,
            barWidth: 1,
            fill: !0,
            fillColor: null,
            align: "left",
            horizontal: !1,
            zero: !0
          },
          shadowSize: 3,
          highlightColor: null
        },
        grid: {
          show: !0,
          aboveData: !1,
          color: "#545454",
          backgroundColor: null,
          borderColor: null,
          tickColor: null,
          margin: 0,
          labelMargin: 5,
          axisMargin: 8,
          borderWidth: 2,
          minBorderMargin: null,
          markings: null,
          markingsColor: "#f4f4f4",
          markingsLineWidth: 2,
          clickable: !1,
          hoverable: !1,
          autoHighlight: !0,
          mouseActiveRadius: 10
        },
        interaction: {
          redrawOverlayInterval: 1e3 / 60
        },
        hooks: {}
      },
      ee = null,
      te = null,
      ie = null,
      oe = null,
      ne = null,
      re = [],
      ae = [],
      le = {
        left: 0,
        right: 0,
        top: 0,
        bottom: 0
      },
      se = 0,
      ce = 0,
      he = {
        processOptions: [],
        processRawData: [],
        processDatapoints: [],
        processOffset: [],
        drawBackground: [],
        drawSeries: [],
        draw: [],
        bindEvents: [],
        drawOverlay: [],
        shutdown: []
      },
      ue = this;
    ue.setData = s, ue.setupGrid = w, ue.draw = z, ue.getPlaceholder = function() {
        return i
      }, ue.getCanvas = function() {
        return ee.element
      }, ue.getPlotOffset = function() {
        return le
      }, ue.width = function() {
        return se
      }, ue.height = function() {
        return ce
      }, ue.offset = function() {
        var e = ie.offset();
        return e.left += le.left, e.top += le.top, e
      }, ue.getData = function() {
        return K
      }, ue.getAxes = function() {
        var t = {};
        return e.each(re.concat(ae), function(e, i) {
          i && (t[i.direction + (1 != i.n ? i.n : "") + "axis"] = i)
        }), t
      }, ue.getXAxes = function() {
        return re
      }, ue.getYAxes = function() {
        return ae
      }, ue.c2p = f, ue.p2c = function(e) {
        var t, i, o, n = {};
        for (t = 0; t < re.length; ++t)
          if ((i = re[t]) && i.used && (o = "x" + i.n, null == e[o] && 1 == i.n && (o = "x"), null != e[o])) {
            n.left = i.p2c(e[o]);
            break
          }
        for (t = 0; t < ae.length; ++t)
          if ((i = ae[t]) && i.used && (o = "y" + i.n, null == e[o] && 1 == i.n && (o = "y"), null != e[o])) {
            n.top = i.p2c(e[o]);
            break
          }
        return n
      }, ue.getOptions = function() {
        return Z
      }, ue.highlight = _, ue.unhighlight = Q, ue.triggerRedrawOverlay = X, ue.pointOffset = function(e) {
        return {
          left: parseInt(re[h(e, "x") - 1].p2c(+e.x) + le.left, 10),
          top: parseInt(ae[h(e, "y") - 1].p2c(+e.y) + le.top, 10)
        }
      }, ue.shutdown = m, ue.destroy = function() {
        m(), i.removeData("plot").empty(), K = [], Z = null, ee = null, te = null, ie = null, oe = null, ne = null, re = [], ae = [], he = null, fe = [], ue = null
      }, ue.resize = function() {
        var e = i.width(),
          t = i.height();
        ee.resize(e, t), te.resize(e, t)
      }, ue.hooks = he,
      function() {
        for (var i = {
            Canvas: t
          }, o = 0; o < a.length; ++o) {
          var n = a[o];
          n.init(ue, i), n.options && e.extend(!0, Z, n.options)
        }
      }(),
      function(t) {
        e.extend(!0, Z, t), t && t.colors && (Z.colors = t.colors), null == Z.xaxis.color && (Z.xaxis.color = e.color.parse(Z.grid.color).scale("a", .22).toString()), null == Z.yaxis.color && (Z.yaxis.color = e.color.parse(Z.grid.color).scale("a", .22).toString()), null == Z.xaxis.tickColor && (Z.xaxis.tickColor = Z.grid.tickColor || Z.xaxis.color), null == Z.yaxis.tickColor && (Z.yaxis.tickColor = Z.grid.tickColor || Z.yaxis.color), null == Z.grid.borderColor && (Z.grid.borderColor = Z.grid.color), null == Z.grid.tickColor && (Z.grid.tickColor = e.color.parse(Z.grid.color).scale("a", .22).toString());
        var o, n, r, a = i.css("font-size"),
          s = a ? +a.replace("px", "") : 13,
          c = {
            style: i.css("font-style"),
            size: Math.round(.8 * s),
            variant: i.css("font-variant"),
            weight: i.css("font-weight"),
            family: i.css("font-family")
          };
        for (r = Z.xaxes.length || 1, o = 0; o < r; ++o)(n = Z.xaxes[o]) && !n.tickColor && (n.tickColor = n.color), n = e.extend(!0, {}, Z.xaxis, n), Z.xaxes[o] = n, n.font && (n.font = e.extend({}, c, n.font), n.font.color || (n.font.color = n.color), n.font.lineHeight || (n.font.lineHeight = Math.round(1.15 * n.font.size)));
        for (r = Z.yaxes.length || 1, o = 0; o < r; ++o)(n = Z.yaxes[o]) && !n.tickColor && (n.tickColor = n.color), n = e.extend(!0, {}, Z.yaxis, n), Z.yaxes[o] = n, n.font && (n.font = e.extend({}, c, n.font), n.font.color || (n.font.color = n.color), n.font.lineHeight || (n.font.lineHeight = Math.round(1.15 * n.font.size)));
        for (Z.xaxis.noTicks && null == Z.xaxis.ticks && (Z.xaxis.ticks = Z.xaxis.noTicks), Z.yaxis.noTicks && null == Z.yaxis.ticks && (Z.yaxis.ticks = Z.yaxis.noTicks), Z.x2axis && (Z.xaxes[1] = e.extend(!0, {}, Z.xaxis, Z.x2axis), Z.xaxes[1].position = "top", null == Z.x2axis.min && (Z.xaxes[1].min = null), null == Z.x2axis.max && (Z.xaxes[1].max = null)), Z.y2axis && (Z.yaxes[1] = e.extend(!0, {}, Z.yaxis, Z.y2axis), Z.yaxes[1].position = "right", null == Z.y2axis.min && (Z.yaxes[1].min = null), null == Z.y2axis.max && (Z.yaxes[1].max = null)), Z.grid.coloredAreas && (Z.grid.markings = Z.grid.coloredAreas), Z.grid.coloredAreasColor && (Z.grid.markingsColor = Z.grid.coloredAreasColor), Z.lines && e.extend(!0, Z.series.lines, Z.lines), Z.points && e.extend(!0, Z.series.points, Z.points), Z.bars && e.extend(!0, Z.series.bars, Z.bars), null != Z.shadowSize && (Z.series.shadowSize = Z.shadowSize), null != Z.highlightColor && (Z.series.highlightColor = Z.highlightColor), o = 0; o < Z.xaxes.length; ++o) p(re, o + 1).options = Z.xaxes[o];
        for (o = 0; o < Z.yaxes.length; ++o) p(ae, o + 1).options = Z.yaxes[o];
        for (var h in he) Z.hooks[h] && Z.hooks[h].length && (he[h] = he[h].concat(Z.hooks[h]));
        l(he.processOptions, [Z])
      }(r),
      function() {
        i.css("padding", 0).children().filter(function() {
          return !e(this).hasClass("flot-overlay") && !e(this).hasClass("flot-base")
        }).remove(), "static" == i.css("position") && i.css("position", "relative"), ee = new t("flot-base", i), te = new t("flot-overlay", i), oe = ee.context, ne = te.context, ie = e(te.element).unbind();
        var o = i.data("plot");
        o && (o.shutdown(), te.clear()), i.data("plot", ue)
      }(), s(n), w(), z(), Z.grid.hoverable && (ie.mousemove(E), ie.bind("mouseleave", H)), Z.grid.clickable && ie.click(B), l(he.bindEvents, [ie]);
    var fe = [],
      pe = null
  }

  function o(e, t) {
    return t * Math.floor(e / t)
  }
  var n = Object.prototype.hasOwnProperty;
  e.fn.detach || (e.fn.detach = function() {
    return this.each(function() {
      this.parentNode && this.parentNode.removeChild(this)
    })
  }), t.prototype.resize = function(e, t) {
    if (e <= 0 || t <= 0) throw new Error("Invalid dimensions for plot, width = " + e + ", height = " + t);
    var i = this.element,
      o = this.context,
      n = this.pixelRatio;
    this.width != e && (i.width = e * n, i.style.width = e + "px", this.width = e), this.height != t && (i.height = t * n, i.style.height = t + "px", this.height = t), o.restore(), o.save(), o.scale(n, n)
  }, t.prototype.clear = function() {
    this.context.clearRect(0, 0, this.width, this.height)
  }, t.prototype.render = function() {
    var e = this._textCache;
    for (var t in e)
      if (n.call(e, t)) {
        var i = this.getTextLayer(t),
          o = e[t];
        i.hide();
        for (var r in o)
          if (n.call(o, r)) {
            var a = o[r];
            for (var l in a)
              if (n.call(a, l)) {
                for (var s, c = a[l].positions, h = 0; s = c[h]; h++) s.active ? s.rendered || (i.append(s.element), s.rendered = !0) : (c.splice(h--, 1), s.rendered && s.element.detach());
                0 == c.length && delete a[l]
              }
          }
        i.show()
      }
  }, t.prototype.getTextLayer = function(t) {
    var i = this.text[t];
    return null == i && (null == this.textContainer && (this.textContainer = e("<div class='flot-text'></div>").css({
      position: "absolute",
      top: 0,
      left: 0,
      bottom: 0,
      right: 0,
      "font-size": "smaller",
      color: "#545454"
    }).insertAfter(this.element)), i = this.text[t] = e("<div></div>").addClass(t).css({
      position: "absolute",
      top: 0,
      left: 0,
      bottom: 0,
      right: 0
    }).appendTo(this.textContainer)), i
  }, t.prototype.getTextInfo = function(t, i, o, n, r) {
    var a, l, s, c;
    if (i = "" + i, a = "object" == typeof o ? o.style + " " + o.variant + " " + o.weight + " " + o.size + "px/" + o.lineHeight + "px " + o.family : o, null == (l = this._textCache[t]) && (l = this._textCache[t] = {}), null == (s = l[a]) && (s = l[a] = {}), null == (c = s[i])) {
      var h = e("<div></div>").html(i).css({
        position: "absolute",
        "max-width": r,
        top: -9999
      }).appendTo(this.getTextLayer(t));
      "object" == typeof o ? h.css({
        font: a,
        color: o.color
      }) : "string" == typeof o && h.addClass(o), c = s[i] = {
        width: h.outerWidth(!0),
        height: h.outerHeight(!0),
        element: h,
        positions: []
      }, h.detach()
    }
    return c
  }, t.prototype.addText = function(e, t, i, o, n, r, a, l, s) {
    var c = this.getTextInfo(e, o, n, r, a),
      h = c.positions;
    "center" == l ? t -= c.width / 2 : "right" == l && (t -= c.width), "middle" == s ? i -= c.height / 2 : "bottom" == s && (i -= c.height);
    for (var u, f = 0; u = h[f]; f++)
      if (u.x == t && u.y == i) return void(u.active = !0);
    u = {
      active: !0,
      rendered: !1,
      element: h.length ? c.element.clone() : c.element,
      x: t,
      y: i
    }, h.push(u), u.element.css({
      top: Math.round(i),
      left: Math.round(t),
      "text-align": l
    })
  }, t.prototype.removeText = function(e, t, i, o, r, a) {
    if (null == o) {
      var l = this._textCache[e];
      if (null != l)
        for (var s in l)
          if (n.call(l, s)) {
            var c = l[s];
            for (var h in c)
              if (n.call(c, h))
                for (var u = c[h].positions, f = 0; p = u[f]; f++) p.active = !1
          }
    } else
      for (var p, u = this.getTextInfo(e, o, r, a).positions, f = 0; p = u[f]; f++) p.x == t && p.y == i && (p.active = !1)
  }, e.plot = function(t, o, n) {
    return new i(e(t), o, n, e.plot.plugins)
  }, e.plot.version = "0.8.3", e.plot.plugins = [], e.fn.plot = function(t, i) {
    return this.each(function() {
      e.plot(this, t, i)
    })
  }
}(jQuery),
function(e, t, i) {
  "$:nomunge";

  function o(i) {
    !0 === l && (l = i || 1);
    for (var s = r.length - 1; s >= 0; s--) {
      var f = e(r[s]);
      if (f[0] == t || f.is(":visible")) {
        var p = f.width(),
          d = f.height(),
          g = f.data(h);
        !g || p === g.w && d === g.h || (f.trigger(c, [g.w = p, g.h = d]), l = i || !0)
      } else(g = f.data(h)).w = 0, g.h = 0
    }
    null !== n && (l && (null == i || i - l < 1e3) ? n = t.requestAnimationFrame(o) : (n = setTimeout(o, a[u]), l = !1))
  }
  var n, r = [],
    a = e.resize = e.extend(e.resize, {}),
    l = !1,
    s = "setTimeout",
    c = "resize",
    h = c + "-special-event",
    u = "pendingDelay",
    f = "activeDelay",
    p = "throttleWindow";
  a[u] = 200, a[f] = 20, a[p] = !0, e.event.special[c] = {
    setup: function() {
      if (!a[p] && this[s]) return !1;
      var t = e(this);
      r.push(this), t.data(h, {
        w: t.width(),
        h: t.height()
      }), 1 === r.length && (n = i, o())
    },
    teardown: function() {
      if (!a[p] && this[s]) return !1;
      for (var t = e(this), i = r.length - 1; i >= 0; i--)
        if (r[i] == this) {
          r.splice(i, 1);
          break
        }
      t.removeData(h), r.length || (l ? cancelAnimationFrame(n) : clearTimeout(n), n = null)
    },
    add: function(t) {
      function o(t, o, r) {
        var a = e(this),
          l = a.data(h) || {};
        l.w = o !== i ? o : a.width(), l.h = r !== i ? r : a.height(), n.apply(this, arguments)
      }
      if (!a[p] && this[s]) return !1;
      var n;
      if (e.isFunction(t)) return n = t, o;
      n = t.handler, t.handler = o
    }
  }, t.requestAnimationFrame || (t.requestAnimationFrame = t.webkitRequestAnimationFrame || t.mozRequestAnimationFrame || t.oRequestAnimationFrame || t.msRequestAnimationFrame || function(e, i) {
    return t.setTimeout(function() {
      e((new Date).getTime())
    }, a[f])
  }), t.cancelAnimationFrame || (t.cancelAnimationFrame = t.webkitCancelRequestAnimationFrame || t.mozCancelRequestAnimationFrame || t.oCancelRequestAnimationFrame || t.msCancelRequestAnimationFrame || clearTimeout)
}(jQuery, this),
function(e) {
  jQuery.plot.plugins.push({
    init: function(e) {
      function t() {
        var t = e.getPlaceholder();
        0 != t.width() && 0 != t.height() && (e.resize(), e.setupGrid(), e.draw())
      }
      e.hooks.bindEvents.push(function(e, i) {
        e.getPlaceholder().resize(t)
      }), e.hooks.shutdown.push(function(e, i) {
        e.getPlaceholder().unbind("resize", t)
      })
    },
    options: {},
    name: "resize",
    version: "1.0"
  })
}(),
function(e) {
  function t(e, t, i, o) {
    var n = "categories" == t.xaxis.options.mode,
      r = "categories" == t.yaxis.options.mode;
    if (n || r) {
      var a = o.format;
      if (!a) {
        var l = t;
        if ((a = []).push({
            x: !0,
            number: !0,
            required: !0
          }), a.push({
            y: !0,
            number: !0,
            required: !0
          }), l.bars.show || l.lines.show && l.lines.fill) {
          var s = !!(l.bars.show && l.bars.zero || l.lines.show && l.lines.zero);
          a.push({
            y: !0,
            number: !0,
            required: !1,
            defaultValue: 0,
            autoscale: s
          }), l.bars.horizontal && (delete a[a.length - 1].y, a[a.length - 1].x = !0)
        }
        o.format = a
      }
      for (var c = 0; c < a.length; ++c) a[c].x && n && (a[c].number = !1), a[c].y && r && (a[c].number = !1)
    }
  }

  function i(e) {
    var t = -1;
    for (var i in e) e[i] > t && (t = e[i]);
    return t + 1
  }

  function o(e) {
    var t = [];
    for (var i in e.categories) {
      var o = e.categories[i];
      o >= e.min && o <= e.max && t.push([o, i])
    }
    return t.sort(function(e, t) {
      return e[0] - t[0]
    }), t
  }

  function n(t, i, n) {
    if ("categories" == t[i].options.mode) {
      if (!t[i].categories) {
        var a = {},
          l = t[i].options.categories || {};
        if (e.isArray(l))
          for (var s = 0; s < l.length; ++s) a[l[s]] = s;
        else
          for (var c in l) a[c] = l[c];
        t[i].categories = a
      }
      t[i].options.ticks || (t[i].options.ticks = o), r(n, i, t[i].categories)
    }
  }

  function r(e, t, o) {
    for (var n = e.points, r = e.pointsize, a = e.format, l = t.charAt(0), s = i(o), c = 0; c < n.length; c += r)
      if (null != n[c])
        for (var h = 0; h < r; ++h) {
          var u = n[c + h];
          null != u && a[h][l] && (u in o || (o[u] = s, ++s), n[c + h] = o[u])
        }
  }

  function a(e, t, i) {
    n(t, "xaxis", i), n(t, "yaxis", i)
  }
  e.plot.plugins.push({
    init: function(e) {
      e.hooks.processRawData.push(t), e.hooks.processDatapoints.push(a)
    },
    options: {
      xaxis: {
        categories: null
      },
      yaxis: {
        categories: null
      }
    },
    name: "categories",
    version: "1.0"
  })
}(jQuery),
function(e) {
  var t = 10,
    i = .95,
    o = {
      series: {
        pie: {
          show: !1,
          radius: "auto",
          innerRadius: 0,
          startAngle: 1.5,
          tilt: 1,
          shadow: {
            left: 5,
            top: 15,
            alpha: .02
          },
          offset: {
            top: 0,
            left: "auto"
          },
          stroke: {
            color: "#fff",
            width: 1
          },
          label: {
            show: "auto",
            formatter: function(e, t) {
              return "<div style='font-size:x-small;text-align:center;padding:2px;color:" + t.color + ";'>" + e + "<br/>" + Math.round(t.percent) + "%</div>"
            },
            radius: 1,
            background: {
              color: null,
              opacity: 0
            },
            threshold: 0
          },
          combine: {
            threshold: -1,
            color: null,
            label: "Other"
          },
          highlight: {
            opacity: .5
          }
        }
      }
    };
  e.plot.plugins.push({
    init: function(o) {
      function n(t, i, o) {
        M || (M = !0, x = t.getCanvas(), v = e(x).parent(), b = t.getOptions(), t.setData(r(t.getData())))
      }

      function r(t) {
        for (var i = 0, o = 0, n = 0, r = b.series.pie.combine.color, a = [], l = 0; l < t.length; ++l) s = t[l].data, e.isArray(s) && 1 == s.length && (s = s[0]), e.isArray(s) ? !isNaN(parseFloat(s[1])) && isFinite(s[1]) ? s[1] = +s[1] : s[1] = 0 : s = !isNaN(parseFloat(s)) && isFinite(s) ? [1, +s] : [1, 0], t[l].data = [s];
        for (l = 0; l < t.length; ++l) i += t[l].data[0][1];
        for (l = 0; l < t.length; ++l)(s = t[l].data[0][1]) / i <= b.series.pie.combine.threshold && (o += s, n++, r || (r = t[l].color));
        for (l = 0; l < t.length; ++l) {
          var s = t[l].data[0][1];
          (n < 2 || s / i > b.series.pie.combine.threshold) && a.push(e.extend(t[l], {
            data: [
              [1, s]
            ],
            color: t[l].color,
            label: t[l].label,
            angle: s * Math.PI * 2 / i,
            percent: s / (i / 100)
          }))
        }
        return n > 1 && a.push({
          data: [
            [1, o]
          ],
          color: r,
          label: b.series.pie.combine.label,
          angle: o * Math.PI * 2 / i,
          percent: o / (i / 100)
        }), a
      }

      function a(o, n) {
        function r() {
          T.clearRect(0, 0, a, s), v.children().filter(".pieLabel, .pieLabelBackground").remove()
        }
        if (v) {
          var a = o.getPlaceholder().width(),
            s = o.getPlaceholder().height(),
            c = v.children().filter(".legend").children().width() || 0;
          T = n, M = !1, k = Math.min(a, s / b.series.pie.tilt) / 2, w = s / 2 + b.series.pie.offset.top, y = a / 2, "auto" == b.series.pie.offset.left ? (b.legend.position.match("w") ? y += c / 2 : y -= c / 2, y < k ? y = k : y > a - k && (y = a - k)) : y += b.series.pie.offset.left;
          var h = o.getData(),
            u = 0;
          do {
            u > 0 && (k *= i), u += 1, r(), b.series.pie.tilt <= .8 && function() {
              var e = b.series.pie.shadow.left,
                t = b.series.pie.shadow.top,
                i = b.series.pie.shadow.alpha,
                o = b.series.pie.radius > 1 ? b.series.pie.radius : k * b.series.pie.radius;
              if (!(o >= a / 2 - e || o * b.series.pie.tilt >= s / 2 - t || o <= 10)) {
                T.save(), T.translate(e, t), T.globalAlpha = i, T.fillStyle = "#000", T.translate(y, w), T.scale(1, b.series.pie.tilt);
                for (var n = 1; n <= 10; n++) T.beginPath(), T.arc(0, 0, o, 0, 2 * Math.PI, !1), T.fill(), o -= n;
                T.restore()
              }
            }()
          } while (! function() {
              function t(e, t, i) {
                e <= 0 || isNaN(e) || (i ? T.fillStyle = t : (T.strokeStyle = t, T.lineJoin = "round"), T.beginPath(), Math.abs(e - 2 * Math.PI) > 1e-9 && T.moveTo(0, 0), T.arc(0, 0, o, n, n + e / 2, !1), T.arc(0, 0, o, n + e / 2, n + e, !1), T.closePath(), n += e, i ? T.fill() : T.stroke())
              }
              var i = Math.PI * b.series.pie.startAngle,
                o = b.series.pie.radius > 1 ? b.series.pie.radius : k * b.series.pie.radius;
              T.save(), T.translate(y, w), T.scale(1, b.series.pie.tilt), T.save();
              for (var n = i, r = 0; r < h.length; ++r) h[r].startAngle = n, t(h[r].angle, h[r].color, !0);
              if (T.restore(), b.series.pie.stroke.width > 0) {
                for (T.save(), T.lineWidth = b.series.pie.stroke.width, n = i, r = 0; r < h.length; ++r) t(h[r].angle, b.series.pie.stroke.color, !1);
                T.restore()
              }
              return l(T), T.restore(), !b.series.pie.label.show || function() {
                for (var t = i, o = b.series.pie.label.radius > 1 ? b.series.pie.label.radius : k * b.series.pie.label.radius, n = 0; n < h.length; ++n) {
                  if (h[n].percent >= 100 * b.series.pie.label.threshold && ! function(t, i, n) {
                      if (0 == t.data[0][1]) return !0;
                      var r, l = b.legend.labelFormatter,
                        c = b.series.pie.label.formatter;
                      r = l ? l(t.label, t) : t.label, c && (r = c(r, t));
                      var h = (i + t.angle + i) / 2,
                        u = y + Math.round(Math.cos(h) * o),
                        f = w + Math.round(Math.sin(h) * o) * b.series.pie.tilt,
                        p = "<span class='pieLabel' id='pieLabel" + n + "' style='position:absolute;top:" + f + "px;left:" + u + "px;'>" + r + "</span>";
                      v.append(p);
                      var d = v.children("#pieLabel" + n),
                        g = f - d.height() / 2,
                        m = u - d.width() / 2;
                      if (d.css("top", g), d.css("left", m), 0 - g > 0 || 0 - m > 0 || s - (g + d.height()) < 0 || a - (m + d.width()) < 0) return !1;
                      if (0 != b.series.pie.label.background.opacity) {
                        var x = b.series.pie.label.background.color;
                        null == x && (x = t.color);
                        var k = "top:" + g + "px;left:" + m + "px;";
                        e("<div class='pieLabelBackground' style='position:absolute;width:" + d.width() + "px;height:" + d.height() + "px;" + k + "background-color:" + x + ";'></div>").css("opacity", b.series.pie.label.background.opacity).insertBefore(d)
                      }
                      return !0
                    }(h[n], t, n)) return !1;
                  t += h[n].angle
                }
                return !0
              }()
            }() && u < t);
          u >= t && (r(), v.prepend("<div class='error'>Could not draw pie with labels contained inside canvas</div>")), o.setSeries && o.insertLegend && (o.setSeries(h), o.insertLegend())
        }
      }

      function l(e) {
        if (b.series.pie.innerRadius > 0) {
          e.save();
          var t = b.series.pie.innerRadius > 1 ? b.series.pie.innerRadius : k * b.series.pie.innerRadius;
          e.globalCompositeOperation = "destination-out", e.beginPath(), e.fillStyle = b.series.pie.stroke.color, e.arc(0, 0, t, 0, 2 * Math.PI, !1), e.fill(), e.closePath(), e.restore(), e.save(), e.beginPath(), e.strokeStyle = b.series.pie.stroke.color, e.arc(0, 0, t, 0, 2 * Math.PI, !1), e.stroke(), e.closePath(), e.restore()
        }
      }

      function s(e, t) {
        for (var i = !1, o = -1, n = e.length, r = n - 1; ++o < n; r = o)(e[o][1] <= t[1] && t[1] < e[r][1] || e[r][1] <= t[1] && t[1] < e[o][1]) && t[0] < (e[r][0] - e[o][0]) * (t[1] - e[o][1]) / (e[r][1] - e[o][1]) + e[o][0] && (i = !i);
        return i
      }

      function c(e, t) {
        for (var i, n, r = o.getData(), a = o.getOptions(), l = a.series.pie.radius > 1 ? a.series.pie.radius : k * a.series.pie.radius, c = 0; c < r.length; ++c) {
          var h = r[c];
          if (h.pie.show) {
            if (T.save(), T.beginPath(), T.moveTo(0, 0), T.arc(0, 0, l, h.startAngle, h.startAngle + h.angle / 2, !1), T.arc(0, 0, l, h.startAngle + h.angle / 2, h.startAngle + h.angle, !1), T.closePath(), i = e - y, n = t - w, T.isPointInPath) {
              if (T.isPointInPath(e - y, t - w)) return T.restore(), {
                datapoint: [h.percent, h.data],
                dataIndex: 0,
                series: h,
                seriesIndex: c
              }
            } else if (s([
                [0, 0],
                [l * Math.cos(h.startAngle), l * Math.sin(h.startAngle)],
                [l * Math.cos(h.startAngle + h.angle / 4), l * Math.sin(h.startAngle + h.angle / 4)],
                [l * Math.cos(h.startAngle + h.angle / 2), l * Math.sin(h.startAngle + h.angle / 2)],
                [l * Math.cos(h.startAngle + h.angle / 1.5), l * Math.sin(h.startAngle + h.angle / 1.5)],
                [l * Math.cos(h.startAngle + h.angle), l * Math.sin(h.startAngle + h.angle)]
              ], [i, n])) return T.restore(), {
              datapoint: [h.percent, h.data],
              dataIndex: 0,
              series: h,
              seriesIndex: c
            };
            T.restore()
          }
        }
        return null
      }

      function h(e) {
        f("plothover", e)
      }

      function u(e) {
        f("plotclick", e)
      }

      function f(e, t) {
        var i = o.offset(),
          n = c(parseInt(t.pageX - i.left), parseInt(t.pageY - i.top));
        if (b.grid.autoHighlight)
          for (var r = 0; r < C.length; ++r) {
            var a = C[r];
            a.auto != e || n && a.series == n.series || d(a.series)
          }
        n && p(n.series, e);
        var l = {
          pageX: t.pageX,
          pageY: t.pageY
        };
        v.trigger(e, [l, n])
      }

      function p(e, t) {
        var i = g(e); - 1 == i ? (C.push({
          series: e,
          auto: t
        }), o.triggerRedrawOverlay()) : t || (C[i].auto = !1)
      }

      function d(e) {
        null == e && (C = [], o.triggerRedrawOverlay());
        var t = g(e); - 1 != t && (C.splice(t, 1), o.triggerRedrawOverlay())
      }

      function g(e) {
        for (var t = 0; t < C.length; ++t)
          if (C[t].series == e) return t;
        return -1
      }

      function m(e, t) {
        var i = e.getOptions(),
          o = i.series.pie.radius > 1 ? i.series.pie.radius : k * i.series.pie.radius;
        t.save(), t.translate(y, w), t.scale(1, i.series.pie.tilt);
        for (var n = 0; n < C.length; ++n) ! function(e) {
          e.angle <= 0 || isNaN(e.angle) || (t.fillStyle = "rgba(255, 255, 255, " + i.series.pie.highlight.opacity + ")", t.beginPath(), Math.abs(e.angle - 2 * Math.PI) > 1e-9 && t.moveTo(0, 0), t.arc(0, 0, o, e.startAngle, e.startAngle + e.angle / 2, !1), t.arc(0, 0, o, e.startAngle + e.angle / 2, e.startAngle + e.angle, !1), t.closePath(), t.fill())
        }(C[n].series);
        l(t), t.restore()
      }
      var x = null,
        v = null,
        b = null,
        k = null,
        y = null,
        w = null,
        M = !1,
        T = null,
        C = [];
      o.hooks.processOptions.push(function(e, t) {
        t.series.pie.show && (t.grid.show = !1, "auto" == t.series.pie.label.show && (t.legend.show ? t.series.pie.label.show = !1 : t.series.pie.label.show = !0), "auto" == t.series.pie.radius && (t.series.pie.label.show ? t.series.pie.radius = .75 : t.series.pie.radius = 1), t.series.pie.tilt > 1 ? t.series.pie.tilt = 1 : t.series.pie.tilt < 0 && (t.series.pie.tilt = 0))
      }), o.hooks.bindEvents.push(function(e, t) {
        var i = e.getOptions();
        i.series.pie.show && (i.grid.hoverable && t.unbind("mousemove").mousemove(h), i.grid.clickable && t.unbind("click").click(u))
      }), o.hooks.processDatapoints.push(function(e, t, i, o) {
        e.getOptions().series.pie.show && n(e)
      }), o.hooks.drawOverlay.push(function(e, t) {
        e.getOptions().series.pie.show && m(e, t)
      }), o.hooks.draw.push(function(e, t) {
        e.getOptions().series.pie.show && a(e, t)
      })
    },
    options: o,
    name: "pie",
    version: "1.1"
  })
}(jQuery),
function(e) {
  jQuery.plot.plugins.push({
    init: function(e) {
      function t(e, t) {
        for (var i = null, o = 0; o < t.length && e != t[o]; ++o) t[o].stack == e.stack && (i = t[o]);
        return i
      }
      e.hooks.processDatapoints.push(function(e, i, o) {
        if (null != i.stack && !1 !== i.stack) {
          var n = t(i, e.getData());
          if (n) {
            for (var r, a, l, s, c, h, u, f, p = o.pointsize, d = o.points, g = n.datapoints.pointsize, m = n.datapoints.points, x = [], v = i.lines.show, b = i.bars.horizontal, k = p > 2 && (b ? o.format[2].x : o.format[2].y), y = v && i.lines.steps, w = !0, M = b ? 1 : 0, T = b ? 0 : 1, C = 0, A = 0; !(C >= d.length);) {
              if (u = x.length, null == d[C]) {
                for (f = 0; f < p; ++f) x.push(d[C + f]);
                C += p
              } else if (A >= m.length) {
                if (!v)
                  for (f = 0; f < p; ++f) x.push(d[C + f]);
                C += p
              } else if (null == m[A]) {
                for (f = 0; f < p; ++f) x.push(null);
                w = !0, A += g
              } else {
                if (r = d[C + M], a = d[C + T], s = m[A + M], c = m[A + T], h = 0, r == s) {
                  for (f = 0; f < p; ++f) x.push(d[C + f]);
                  x[u + T] += c, h = c, C += p, A += g
                } else if (r > s) {
                  if (v && C > 0 && null != d[C - p]) {
                    for (l = a + (d[C - p + T] - a) * (s - r) / (d[C - p + M] - r), x.push(s), x.push(l + c), f = 2; f < p; ++f) x.push(d[C + f]);
                    h = c
                  }
                  A += g
                } else {
                  if (w && v) {
                    C += p;
                    continue
                  }
                  for (f = 0; f < p; ++f) x.push(d[C + f]);
                  v && A > 0 && null != m[A - g] && (h = c + (m[A - g + T] - c) * (r - s) / (m[A - g + M] - s)), x[u + T] += h, C += p
                }
                w = !1, u != x.length && k && (x[u + 2] += h)
              }
              if (y && u != x.length && u > 0 && null != x[u] && x[u] != x[u - p] && x[u + 1] != x[u - p + 1]) {
                for (f = 0; f < p; ++f) x[u + p + f] = x[u + f];
                x[u + 1] = x[u - p + 1]
              }
            }
            o.points = x
          }
        }
      })
    },
    options: {
      series: {
        stack: null
      }
    },
    name: "stack",
    version: "1.2"
  })
}(),
function(e) {
  jQuery.plot.plugins.push({
    init: function(e) {
      function t(t) {
        o.locked || -1 != o.x && (o.x = -1, e.triggerRedrawOverlay())
      }

      function i(t) {
        if (!o.locked)
          if (e.getSelection && e.getSelection()) o.x = -1;
          else {
            var i = e.offset();
            o.x = Math.max(0, Math.min(t.pageX - i.left, e.width())), o.y = Math.max(0, Math.min(t.pageY - i.top, e.height())), e.triggerRedrawOverlay()
          }
      }
      var o = {
        x: -1,
        y: -1,
        locked: !1
      };
      e.setCrosshair = function(t) {
        if (t) {
          var i = e.p2c(t);
          o.x = Math.max(0, Math.min(i.left, e.width())), o.y = Math.max(0, Math.min(i.top, e.height()))
        } else o.x = -1;
        e.triggerRedrawOverlay()
      }, e.clearCrosshair = e.setCrosshair, e.lockCrosshair = function(t) {
        t && e.setCrosshair(t), o.locked = !0
      }, e.unlockCrosshair = function() {
        o.locked = !1
      }, e.hooks.bindEvents.push(function(e, o) {
        e.getOptions().crosshair.mode && (o.mouseout(t), o.mousemove(i))
      }), e.hooks.drawOverlay.push(function(e, t) {
        var i = e.getOptions().crosshair;
        if (i.mode) {
          var n = e.getPlotOffset();
          if (t.save(), t.translate(n.left, n.top), -1 != o.x) {
            var r = e.getOptions().crosshair.lineWidth % 2 ? .5 : 0;
            if (t.strokeStyle = i.color, t.lineWidth = i.lineWidth, t.lineJoin = "round", t.beginPath(), -1 != i.mode.indexOf("x")) {
              var a = Math.floor(o.x) + r;
              t.moveTo(a, 0), t.lineTo(a, e.height())
            }
            if (-1 != i.mode.indexOf("y")) {
              var l = Math.floor(o.y) + r;
              t.moveTo(0, l), t.lineTo(e.width(), l)
            }
            t.stroke()
          }
          t.restore()
        }
      }), e.hooks.shutdown.push(function(e, o) {
        o.unbind("mouseout", t), o.unbind("mousemove", i)
      })
    },
    options: {
      crosshair: {
        mode: null,
        color: "rgba(170, 0, 0, 0.80)",
        lineWidth: 1
      }
    },
    name: "crosshair",
    version: "1.0"
  })
}();