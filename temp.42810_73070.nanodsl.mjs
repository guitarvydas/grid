'use strict'

import * as ohm from 'ohm-js';

let verbose = false;

function top (stack) { let v = stack.pop (); stack.push (v); return v; }

function set_top (stack, v) { stack.pop (); stack.push (v); return v; }

let return_value_stack = [];
let rule_name_stack = [];
let depth_prefix = ' ';

function enter_rule (name) {
    if (verbose) {
	console.error (depth_prefix, ["enter", name]);
	depth_prefix += ' ';
    }
    return_value_stack.push ("");
    rule_name_stack.push (name);
}

function set_return (v) {
    set_top (return_value_stack, v);
}

function exit_rule (name) {
    if (verbose) {
	depth_prefix = depth_prefix.substr (1);
	console.error (depth_prefix, ["exit", name]);
    }
    rule_name_stack.pop ();
    return return_value_stack.pop ()
}

const grammar = String.raw`
gridprepass {
  main = stuff+
  stuff =
    | nl      -- nl
    | string  -- string
    | keyword -- keyword
    | comment -- comment
    | ident   -- ident
    | any     -- other
    
  keyword =
    | caseInsensitive<"with"> ~idtail
    | caseInsensitive<"type"> ~idtail
    | caseInsensitive<"to"> ~idtail
    | caseInsensitive<"then"> ~idtail
    | caseInsensitive<"text"> ~idtail
    | caseInsensitive<"super"> ~idtail
    | caseInsensitive<"subprocess"> ~idtail
    | caseInsensitive<"step"> ~idtail
    | caseInsensitive<"return"> ~idtail
    | caseInsensitive<"push"> ~idtail
    | caseInsensitive<"privatehelper"> ~idtail
    | caseInsensitive<"output"> ~idtail
    | caseInsensitive<"or"> ~idtail
    | caseInsensitive<"of"> ~idtail
    | caseInsensitive<"number"> ~idtail
    | caseInsensitive<"not"> ~idtail
    | caseInsensitive<"new"> ~idtail
    | caseInsensitive<"mod"> ~idtail
    | caseInsensitive<"let"> ~idtail
    | caseInsensitive<"label"> ~idtail
    | caseInsensitive<"input"> ~idtail
    | caseInsensitive<"init"> ~idtail
    | caseInsensitive<"index"> ~idtail
    | caseInsensitive<"in"> ~idtail
    | caseInsensitive<"if"> ~idtail
    | caseInsensitive<"function"> ~idtail
    | caseInsensitive<"for"> ~idtail
    | caseInsensitive<"end"> ~idtail
    | caseInsensitive<"elseif"> ~idtail
    | caseInsensitive<"else"> ~idtail
    | caseInsensitive<"do"> ~idtail
    | caseInsensitive<"dim"> ~idtail
    | caseInsensitive<"define"> ~idtail
    | caseInsensitive<"as"> ~idtail
    | caseInsensitive<"and"> ~idtail

  string = "\"" strchar* "\""
  strchar =
    | "\"" "\"" -- escapedquote
    | ~"\"" any -- other
    
  ident = (letter | "_") idtail*
  idtail = alnum | "_"
  comment = "'" (~nl any)* nl
  nl = ( "\r\n" | "\n")
}
`;

let args = {};
function resetArgs () {
    args = {};
}
function memoArg (name, accessorString) {
    args [name] = accessorString;
};
function fetchArg (name) {
    return args [name];
}

function downcase (s) {
    return s.toLowerCase (s);
}

let line = 0;
function incnl () {
    line += 1;
    return `⎩${line}⎭`
}

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
keyword : function (kw,) {
enter_rule ("keyword");
    set_return (`${downcase (`${kw.rwr ()}`,)}`);
return exit_rule ("keyword");
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
    set_return (`${downcase (`${c.rwr ()}${tailcs.rwr ().join ('')}`,)}`);
return exit_rule ("ident");
},
idtail : function (c,) {
enter_rule ("idtail");
    set_return (`${c.rwr ()}`);
return exit_rule ("idtail");
},
comment : function (q,cs,nl,) {
enter_rule ("comment");
    set_return (`⎝${cs.rwr ().join ('')}⎠  ${incnl ()}`);
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
import * as fs from 'fs';

let terminated = false;

function xbreak () {
    terminated = true;
    return '';
}

function xcontinue () {
    terminated = false;
    return '';
}
    
function is_terminated () {
    return terminated;
}
function expand (src, parser) {
    let cst = parser.match (src);
    if (cst.failed ()) {
	//th  row Error (`${cst.message}\ngrammar=${grammarname (grammar)}\nsrc=\n${src}`);
	throw Error (cst.message);
    }
    let sem = parser.createSemantics ();
    sem.addOperation ('rwr', _rewrite);
    return sem (cst).rwr ();
}

function grammarname (s) {
    let n = s.search (/{/);
    return s.substr (0, n).replaceAll (/\n/g,'').trim ();
}

try {
    const argv = process.argv.slice(2);
    let srcFilename = argv[0];
    if ('-' == srcFilename) { srcFilename = 0 }
    let src = fs.readFileSync(srcFilename, 'utf-8');
    try {
	let parser = ohm.grammar (grammar);
	let s = src;
	xcontinue ();
	while (! is_terminated ()) {
	    xbreak ();
	    s = expand (s, parser);
	}
	console.log (s);
	process.exit (0);
    } catch (e) {
	//console.error (`${e}\nargv=${argv}\ngrammar=${grammarname (grammar)}\src=\n${src}`);
	console.error (`${e}\n\ngrammar = "${grammarname (grammar)}\n"`);
	process.exit (1);
    }
} catch (e) {
    console.error (`${e}\n\ngrammar = "${grammarname (grammar)}"\n`);
    process.exit (1);
}

