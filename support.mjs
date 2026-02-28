function downcase (s) {
    return s.toLowerCase (s);
}

let line = 0;
function incnl () {
    line += 1;
    return `⎩${line}⎭`
}

// semantic checks
function semcheckideq (id1, id2) {
    if (id1 != id2) {
	throw new Error (`ending name ${id2} does not match function name ${id1}`);
    }
    return "";
}
