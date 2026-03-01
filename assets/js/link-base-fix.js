(function () {
  function getBasePath() {
    var path = window.location.pathname || "/";
    if (path.endsWith(".html")) {
      return path.slice(0, path.lastIndexOf("/") + 1);
    }
    return path.endsWith("/") ? path : path + "/";
  }

  function isInternalHtmlLink(rawHref) {
    if (!rawHref) return false;
    if (rawHref.startsWith("http://") || rawHref.startsWith("https://")) return false;
    if (rawHref.startsWith("//")) return false;
    if (rawHref.startsWith("mailto:") || rawHref.startsWith("tel:")) return false;
    if (rawHref.startsWith("#")) return false;

    var clean = rawHref.split("#")[0].split("?")[0];
    return clean.endsWith(".html");
  }

  function normalizeHref(rawHref, basePath) {
    var hash = "";
    var query = "";
    var path = rawHref;

    var hashIndex = path.indexOf("#");
    if (hashIndex >= 0) {
      hash = path.slice(hashIndex);
      path = path.slice(0, hashIndex);
    }

    var queryIndex = path.indexOf("?");
    if (queryIndex >= 0) {
      query = path.slice(queryIndex);
      path = path.slice(0, queryIndex);
    }

    if (path.startsWith("/")) {
      return path + query + hash;
    }

    path = path.replace(/^\.\//, "");
    return basePath + path + query + hash;
  }

  document.addEventListener("DOMContentLoaded", function () {
    var basePath = getBasePath();
    var links = document.querySelectorAll("a[href]");

    links.forEach(function (link) {
      var rawHref = link.getAttribute("href");
      if (!isInternalHtmlLink(rawHref)) return;

      link.setAttribute("href", normalizeHref(rawHref, basePath));
    });
  });
})();
