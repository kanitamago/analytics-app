window.onload = function(){
  add_tableClass();
  show_heatmap();
  show_hist();
  show_scatter();
};

function add_tableClass(){
  var tables = document.getElementsByClassName("dataframe");
  for (var i = 0; i < tables.length; i++) {
    tables[i].classList.add("table");
    tables[i].classList.add("table-striped");
    tables[i].classList.add("table-sm");
  };
  var theads = document.getElementsByTagName("thead");
  for (var i = 0; i < theads.length; i++) {
    theads[i].classList.add("table-dark");
  };
};

function show_heatmap(){
  $("#heat-btn").on("click", function() {
  $("#heat-image").slideToggle();
});
}

function show_hist(){
  $("#hist-btn").on("click", function() {
  $("#hist-image").slideToggle();
});
}

function show_scatter(){
  $("#scatter-btn").on("click", function() {
  $("#scatter-image").slideToggle();
});
}
