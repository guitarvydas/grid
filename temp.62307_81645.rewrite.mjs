let parameters = {};
function pushParameter (name, v) {
    if (!parameters [name]) {
        parameters [name] = [];
    }
    parameters [name].push (v);
}
function popParameter (name) {
    parameters [name].pop ();
}
function getParameter (name) {
    let top = parameters [name].pop ();
    parameters [name].push (top);
    return top;
}


let _rewrite = {

main : function (stuff,) {
enter_rule ("main");
    set_return (`${stuff.rwr ().join ('')}`);
return exit_rule ("main");
},
stuff : function (x,) {
enter_rule ("stuff");
    set_return (`${x.rwr ()}`);
return exit_rule ("stuff");
},
keyword_with : function (s,) {
enter_rule ("keyword_with");
    set_return (`with`);
return exit_rule ("keyword_with");
},
keyword_type : function (s,) {
enter_rule ("keyword_type");
    set_return (`Type`);
return exit_rule ("keyword_type");
},
keyword_to : function (s,) {
enter_rule ("keyword_to");
    set_return (`to`);
return exit_rule ("keyword_to");
},
keyword_then : function (s,) {
enter_rule ("keyword_then");
    set_return (`Then`);
return exit_rule ("keyword_then");
},
keyword_text : function (s,) {
enter_rule ("keyword_text");
    set_return (`text`);
return exit_rule ("keyword_text");
},
keyword_super : function (s,) {
enter_rule ("keyword_super");
    set_return (`Super`);
return exit_rule ("keyword_super");
},
keyword_subprocess : function (s,) {
enter_rule ("keyword_subprocess");
    set_return (`Subprocess`);
return exit_rule ("keyword_subprocess");
},
keyword_step : function (s,) {
enter_rule ("keyword_step");
    set_return (`step`);
return exit_rule ("keyword_step");
},
keyword_return : function (s,) {
enter_rule ("keyword_return");
    set_return (`Return`);
return exit_rule ("keyword_return");
},
keyword_push : function (s,) {
enter_rule ("keyword_push");
    set_return (`Push`);
return exit_rule ("keyword_push");
},
keyword_privatehelper : function (s,) {
enter_rule ("keyword_privatehelper");
    set_return (`PrivateHelper`);
return exit_rule ("keyword_privatehelper");
},
keyword_output : function (s,) {
enter_rule ("keyword_output");
    set_return (`Output`);
return exit_rule ("keyword_output");
},
keyword_oreq : function (s,) {
enter_rule ("keyword_oreq");
    set_return (`or=`);
return exit_rule ("keyword_oreq");
},
keyword_or : function (s,) {
enter_rule ("keyword_or");
    set_return (`OR`);
return exit_rule ("keyword_or");
},
keyword_of : function (s,) {
enter_rule ("keyword_of");
    set_return (`of`);
return exit_rule ("keyword_of");
},
keyword_number : function (s,) {
enter_rule ("keyword_number");
    set_return (`number`);
return exit_rule ("keyword_number");
},
keyword_not : function (s,) {
enter_rule ("keyword_not");
    set_return (`not`);
return exit_rule ("keyword_not");
},
keyword_new : function (s,) {
enter_rule ("keyword_new");
    set_return (`new`);
return exit_rule ("keyword_new");
},
keyword_mod : function (s,) {
enter_rule ("keyword_mod");
    set_return (`mod`);
return exit_rule ("keyword_mod");
},
keyword_let : function (s,) {
enter_rule ("keyword_let");
    set_return (`Let`);
return exit_rule ("keyword_let");
},
keyword_label : function (s,) {
enter_rule ("keyword_label");
    set_return (`Label`);
return exit_rule ("keyword_label");
},
keyword_input : function (s,) {
enter_rule ("keyword_input");
    set_return (`Input`);
return exit_rule ("keyword_input");
},
keyword_init : function (s,) {
enter_rule ("keyword_init");
    set_return (`init`);
return exit_rule ("keyword_init");
},
keyword_index : function (s,) {
enter_rule ("keyword_index");
    set_return (`index`);
return exit_rule ("keyword_index");
},
keyword_in : function (s,) {
enter_rule ("keyword_in");
    set_return (`in`);
return exit_rule ("keyword_in");
},
keyword_if : function (s,) {
enter_rule ("keyword_if");
    set_return (`If`);
return exit_rule ("keyword_if");
},
keyword_function : function (s,) {
enter_rule ("keyword_function");
    set_return (`Function`);
return exit_rule ("keyword_function");
},
keyword_for : function (s,) {
enter_rule ("keyword_for");
    set_return (`For`);
return exit_rule ("keyword_for");
},
keyword_end : function (s,) {
enter_rule ("keyword_end");
    set_return (`End`);
return exit_rule ("keyword_end");
},
keyword_elseif : function (s,) {
enter_rule ("keyword_elseif");
    set_return (`ElseIf`);
return exit_rule ("keyword_elseif");
},
keyword_else : function (s,) {
enter_rule ("keyword_else");
    set_return (`Else`);
return exit_rule ("keyword_else");
},
keyword_do : function (s,) {
enter_rule ("keyword_do");
    set_return (`do`);
return exit_rule ("keyword_do");
},
keyword_dim : function (s,) {
enter_rule ("keyword_dim");
    set_return (`dim`);
return exit_rule ("keyword_dim");
},
keyword_define : function (s,) {
enter_rule ("keyword_define");
    set_return (`Define`);
return exit_rule ("keyword_define");
},
keyword_as : function (s,) {
enter_rule ("keyword_as");
    set_return (`as`);
return exit_rule ("keyword_as");
},
keyword_and : function (s,) {
enter_rule ("keyword_and");
    set_return (`AND`);
return exit_rule ("keyword_and");
},
string : function (dqL,cs,dqR,) {
enter_rule ("string");
    set_return (`"${cs.rwr ().join ('')}"`);
return exit_rule ("string");
},
strchar_escapedquote : function (dq1,dq2,) {
enter_rule ("strchar_escapedquote");
    set_return (`\"`);
return exit_rule ("strchar_escapedquote");
},
strchar_other : function (c,) {
enter_rule ("strchar_other");
    set_return (`${c.rwr ()}`);
return exit_rule ("strchar_other");
},
ident : function (c,tailcs,) {
enter_rule ("ident");
    set_return (`❲${downcase (`${c.rwr ()}${tailcs.rwr ().join ('')}`,)}❳`);
return exit_rule ("ident");
},
idtail : function (c,) {
enter_rule ("idtail");
    set_return (`${c.rwr ()}`);
return exit_rule ("idtail");
},
comment : function (q,cs,nl,) {
enter_rule ("comment");
    set_return (`⎝${cs.rwr ().join ('')}⎠  ${incnl ()}\n`);
return exit_rule ("comment");
},
nl : function (c,) {
enter_rule ("nl");
    set_return (`  ${incnl ()}\n`);
return exit_rule ("nl");
},
_terminal: function () { return this.sourceString; },
_iter: function (...children) { return children.map(c => c.rwr ()); }
}
