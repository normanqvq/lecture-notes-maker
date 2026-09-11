"""
Template for a cheatsheet content module.  Copy next to your snippets, fill in,
then:  python assets/build_cheatsheet.py content.py --out X.pdf --check --measure
"""
from cheatsheet import code, sec, sub, fig, header, tf_table, steps, table, tree_svg

TITLE = "COURSE Quiz N Cheatsheet"      # browser/PDF title
CSS_EXTRA = ""                           # e.g. "pre.code { font-size: 4.9pt; }"
LAYOUT = {}                              # override cheatsheet.LAYOUT_DEFAULTS keys, e.g. {"columns": 4}

# ---- code snippets: blank line = new breakable box; '!! ' = yellow key line; '//!' = red comment ----
S = {}
S['example'] = r'''
void insertHead(int x) {                 // O(1)
    ListNode *n = new ListNode(x);       // 1. create
!!     n->_next = _head;                    // 2. link new -> old head (BEFORE 3)
!!     _head = n;                           // 3. move head
    _size++;                             // 4.
}   //! swapping 2 and 3 loses the whole list
'''

# ---- side 1 ----
P1 = []
P1.append(header("COURSE Full Name", "Quiz N Cheatsheet",
                 "AYxx/xx &middot; topics &middot; <r>red = 考点/陷阱</r> &middot; <y>yellow = key lines</y>"))
P1.append(sec("1. Section title (marks it carries in past papers)"))
P1.append(sub("Sub-topic"))
P1.append(code(S['example']))
P1.append("<p>Prose: one idea per sentence. Inline code with <k>k</k> tags, exam traps in <r>red</r>.</p>")
P1.append(tf_table([
    ("A class can have more than one constructor", "T"),
    ("A constructor must be public", "F"),
]))
P1.append(table(["code", "Steps"], [
    ("for(i=0;i&lt;n;i++) O(1);\nreturn f(n/2);", steps("Step 1: T(n)=T(n/2)+n.", "Step 2: n+n/2+n/4+&hellip; &le; 2n.", "<b>&rArr; O(n)</b>")),
], mono_first=True))

# ---- side 2 ----
P2 = []
P2.append(sec("2. Next section"))
P2.append(fig(tree_svg({41: (150, 12), 20: (75, 40), 65: (225, 40)}, [(41, 20), (41, 65)], badges={41: "h=1"}),
              "Caption: what the reader should notice."))

PAGES = [P1, P2]
