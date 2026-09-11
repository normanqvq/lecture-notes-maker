"""
Worked example: CS2040C (NUS, Data Structures & Algorithms) Quiz 1 cheatsheet, AY25/26 S1.
Scope: C++/OOP, linked list, ADT, Big O, searching, sorting, BST (no AVL).
Weighting decided from 8 past papers (Part A = 6 complexity MCQs, Part B = 10 T/F,
Part C = sorting detective, Part D = fill-in code).  Build:

    python ../../../assets/build_cheatsheet.py content.py --out CS2040C_Quiz1_Cheatsheet.pdf --check
"""
from cheatsheet import code, sec, sub, fig, tree_svg
from snippets import S

TITLE = "CS2040C Quiz 1 Cheatsheet"
CSS_EXTRA = "body { line-height: 1.08; } th, td { padding: 0.35pt 1.4pt; } pre.code { line-height: 1.05; margin: 1pt 0; } p { margin-bottom: 0.9pt; } ul { margin-bottom: 0.9pt; } h1 { margin: 1.3pt 0 0.5pt; } h2 { margin: 1pt 0 0.3pt; } table { margin: 0.8pt 0 1.1pt; } .fig { margin: 0.5pt 0; }"
LAYOUT = {"margin": "3.5mm 4mm", "page_height": "203mm", "column_gap": "2.2mm"}

# ---------------- SVG figures ----------------
def tree_svg():
    nodes = {41:(150,12),20:(75,40),65:(225,40),11:(37,68),29:(112,68),50:(187,68),91:(262,68),32:(135,96),72:(240,96),99:(285,96)}
    edges = [(41,20),(41,65),(20,11),(20,29),(65,50),(65,91),(29,32),(91,72),(91,99)]
    hs = {41:3,20:2,65:2,11:0,29:1,50:0,91:1,32:0,72:0,99:0}
    s = ['<svg viewBox="0 0 330 112" width="34mm" xmlns="http://www.w3.org/2000/svg">']
    for a,b in edges:
        (x1,y1),(x2,y2) = nodes[a],nodes[b]
        s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333" stroke-width="1"/>')
    for k,(x,y) in nodes.items():
        s.append(f'<circle cx="{x}" cy="{y}" r="9.5" fill="#fff8d6" stroke="#000" stroke-width="1"/>')
        s.append(f'<text x="{x}" y="{y+3}" font-size="8.5" text-anchor="middle" font-weight="bold">{k}</text>')
        s.append(f'<text x="{x+11}" y="{y-5}" font-size="6.5" fill="#c00000">h={hs[k]}</text>')
    s.append('<text x="150" y="0" font-size="6.5" text-anchor="middle" dy="-1"></text>')
    s.append('<text x="300" y="14" font-size="6.5" fill="#0b2d6b">root=41, n=10</text>')
    s.append('<text x="300" y="23" font-size="6.5" fill="#0b2d6b">height=3</text>')
    s.append('<text x="300" y="32" font-size="6.5" fill="#0b2d6b">leaves: 11 32</text>')
    s.append('<text x="300" y="41" font-size="6.5" fill="#0b2d6b">50 72 99</text>')
    s.append('</svg>')
    return ''.join(s)

def delete_svg():
    def mini(ox, nodes, edges, title, hi=None):
        out = [f'<text x="{ox+60}" y="8" font-size="7" text-anchor="middle" font-weight="bold">{title}</text>']
        for a,b in edges:
            (x1,y1),(x2,y2) = nodes[a],nodes[b]
            out.append(f'<line x1="{ox+x1}" y1="{y1}" x2="{ox+x2}" y2="{y2}" stroke="#333" stroke-width="1"/>')
        for k,(x,y) in nodes.items():
            fill = '#ffd2d2' if k==hi else '#fff8d6'
            out.append(f'<circle cx="{ox+x}" cy="{y}" r="8" fill="{fill}" stroke="#000" stroke-width="1"/>')
            out.append(f'<text x="{ox+x}" y="{y+3}" font-size="7.5" text-anchor="middle" font-weight="bold">{k}</text>')
        return ''.join(out)
    s = ['<svg viewBox="0 0 270 78" width="26mm" xmlns="http://www.w3.org/2000/svg">']
    n1 = {65:(60,22),50:(30,46),91:(90,46),72:(72,70),99:(108,70)}
    s.append(mini(0, n1, [(65,50),(65,91),(91,72),(91,99)], 'delete(65): 2 children', 65))
    s.append('<text x="135" y="45" font-size="8" text-anchor="middle">&#8594;</text>')
    n2 = {72:(60,22),50:(30,46),91:(90,46),99:(108,70)}
    s.append(mini(140, n2, [(72,50),(72,91),(91,99)], 'copy successor 72, delete old 72', 72))
    s.append('</svg>')
    return ''.join(s)

def rec_svg():
    s = ['<svg viewBox="0 0 250 62" width="36mm" xmlns="http://www.w3.org/2000/svg">']
    def box(x,y,w,t): 
        return f'<rect x="{x-w/2}" y="{y-6}" width="{w}" height="12" fill="#eef3ff" stroke="#333" stroke-width="0.7"/><text x="{x}" y="{y+3}" font-size="7" text-anchor="middle">{t}</text>'
    s.append(box(90,8,30,'cn')); 
    for x in (50,130): s.append(f'<line x1="90" y1="14" x2="{x}" y2="22" stroke="#333" stroke-width="0.7"/>'); s.append(box(x,28,30,'cn/2'))
    for i,x in enumerate((30,70,110,150)):
        px = 50 if i<2 else 130
        s.append(f'<line x1="{px}" y1="34" x2="{x}" y2="42" stroke="#333" stroke-width="0.7"/>'); s.append(box(x,48,28,'cn/4'))
    s.append('<text x="90" y="60" font-size="7" text-anchor="middle">... down to size 1</text>')
    for y,t in ((11,'level cost = cn'),(31,'2 &times; cn/2 = cn'),(51,'4 &times; cn/4 = cn')):
        s.append(f'<text x="172" y="{y}" font-size="7" fill="#c00000">{t}</text>')
    s.append('<text x="172" y="60" font-size="7" font-weight="bold">log&#8322;n levels &#8658; cn&middot;log n</text>')
    s.append('</svg>')
    return ''.join(s)

def list_svg():
    s = ['<svg viewBox="0 0 300 42" width="50mm" xmlns="http://www.w3.org/2000/svg">']
    s.append('<rect x="2" y="6" width="52" height="28" fill="#e8ecf3" stroke="#000" stroke-width="0.8"/>')
    s.append('<text x="28" y="16" font-size="7" text-anchor="middle" font-weight="bold">List (engine)</text>')
    s.append('<text x="28" y="24" font-size="6.5" text-anchor="middle">_size = 3</text>')
    s.append('<text x="28" y="31" font-size="6.5" text-anchor="middle">_head &#9679;</text>')
    xs = [78,158,238]; vals=['123','551','78']; nxt=['&#9679;','&#9679;','NULL']
    for i,x in enumerate(xs):
        s.append(f'<rect x="{x}" y="8" width="34" height="22" fill="#fff8d6" stroke="#000" stroke-width="0.8"/>')
        s.append(f'<rect x="{x+34}" y="8" width="26" height="22" fill="#fff" stroke="#000" stroke-width="0.8"/>')
        s.append(f'<text x="{x+17}" y="22" font-size="7.5" text-anchor="middle" font-weight="bold">{vals[i]}</text>')
        s.append(f'<text x="{x+47}" y="22" font-size="6.5" text-anchor="middle">{nxt[i]}</text>')
        s.append(f'<text x="{x+17}" y="38" font-size="5.8" text-anchor="middle">_item</text><text x="{x+47}" y="38" font-size="5.8" text-anchor="middle">_next</text>')
        if i<2: s.append(f'<line x1="{x+60}" y1="19" x2="{x+80}" y2="19" stroke="#c00000" stroke-width="1" marker-end="url(#ah)"/>')
    s.append('<line x1="54" y1="28" x2="78" y2="19" stroke="#c00000" stroke-width="1" marker-end="url(#ah)"/>')
    s.append('<text x="0" y="41" font-size="6" fill="#0b2d6b">_tail &#8594; last node</text>')
    s.append('<defs><marker id="ah" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#c00000"/></marker></defs>')
    s.append('</svg>')
    return ''.join(s)


# ---------------- PAGE 1 ----------------
P1 = []
P1.append('''<div class="hdr"><div class="t">CS2040C Data Structures and Algorithms</div><div class="t2">Quiz 1 Cheatsheet</div><div class="s">AY25/26 S1 &middot; C++ &middot; Linked List &middot; ADT &middot; Big O &middot; Sorting &middot; BST &middot; <r>red = 考点/陷阱</r> &middot; <y>yellow = key lines</y></div></div>''')

P1.append(sec('1. C++ Crash Course, Pointers &amp; OOP'))
P1.append(sub('Pointers, new/delete, references'))
P1.append(code(S['ptr']))
P1.append('<p><k>*</k> in a declaration = "is a pointer"; in a statement = dereference. <k>p-&gt;x</k> &equiv; <k>(*p).x</k>. <r>Wild pointer</r> (uninitialised): writing through it segfaults <i>or</i> silently corrupts other data. <k>new</k> memory that no pointer points to = <r>orphan &rArr; memory leak</r>; after <k>delete</k> the pointer is <r>dangling</r>. <k>delete</k> only what you <k>new</k>-ed. <k>malloc/free</k> still work in C++ ("cannot use malloc": <r>F</r>) but <k>new</k> also calls the constructor.</p>')
P1.append(sub('Parameter passing &amp; overloading (slides output = 1 10 10)'))
P1.append(code(S['pass']))
P1.append(sub('Class syntax, constructor, destructor, access'))
P1.append(code(S['class']))
P1.append('''<table><tr><th>access</th><th>own class</th><th>subclass</th><th>friend</th><th>outside</th></tr>
<tr><td><b>private</b> (default in class)</td><td>&#10004;</td><td>&#10008;</td><td>&#10004;</td><td>&#10008;</td></tr>
<tr><td><b>protected</b></td><td>&#10004;</td><td>&#10004;</td><td>&#10004;</td><td>&#10008;</td></tr>
<tr><td><b>public</b> (default in struct)</td><td>&#10004;</td><td>&#10004;</td><td>&#10004;</td><td>&#10004;</td></tr></table>''')
P1.append('<p><b>friend</b> = "let that class access my private &amp; protected": <r>one-directional, not inherited, not transitive</r>. Access depends on <b>where the code is written</b>, not on the object&#39;s type. Class = blueprint; instance = its own copy of the attributes. <b>Encapsulation</b>: data hidden, used via public methods.</p>')
P1.append(sub('Inheritance, override, polymorphism (virtual)'))
P1.append(code(S['inherit']))
P1.append('''<ul>
<li><b>Inheritance</b>: reuse an implementation and change a little behaviour, without copy-paste or editing the original class.</li>
<li><b>Composition</b> (<k>List _ll</k> inside Stack): hide / rename the inner object&#39;s operations.</li>
<li><b>Polymorphism</b>: <k>Animal *a = new Dog(); a-&gt;talk();</k> prints Woof only if <k>talk</k> is <k>virtual</k> in Animal (dispatched by the object&#39;s real type at run time). Child with no own version &rArr; parent&#39;s runs.</li>
<li><r>Parent can&#39;t use child members; only functions (not data members) can be overridden.</r></li></ul>''')
P1.append('<p><b>T/F bank (all appeared in past quizzes):</b></p>')
P1.append('''<table class="tf"><tr><td>A class can have more than one constructor</td><td><t>T</t></td></tr><tr><td>A class can have only one destructor</td><td><t>T</t></td></tr><tr><td>A constructor must be public; it cannot be private or protected</td><td><r>F</r></td></tr><tr><td>A class can be implemented without any attributes</td><td><t>T</t></td></tr><tr><td>If no access specifier is given, class members are public by default (they are <b>private</b>)</td><td><r>F</r></td></tr><tr><td>Parameter declared <k>int &amp;x</k>: x is a pointer to an integer (it is a reference)</td><td><r>F</r></td></tr><tr><td>A child class can access the private attributes of its parent directly (needs protected / friend)</td><td><r>F</r></td></tr><tr><td>A protected member cannot be accessed by the member functions of that class</td><td><r>F</r></td></tr><tr><td>Protected members of A are accessible to any class that A declared as friend</td><td><t>T</t></td></tr><tr><td>A private member is impossible to access from other classes (friend can)</td><td><r>F</r></td></tr><tr><td>A inherits B and B inherits C is called multiple inheritance (it is <b>multilevel</b>)</td><td><r>F</r></td></tr><tr><td>A parent class can have more than one child class</td><td><t>T</t></td></tr><tr><td>A subclass cannot override its parent&#39;s member functions</td><td><r>F</r></td></tr><tr><td>A virtual function can only be accessed by itself and its subclasses (virtual &ne; access control)</td><td><r>F</r></td></tr><tr><td>In C++, inheritance is not compatible with template</td><td><r>F</r></td></tr><tr><td>We cannot overload the arithmetic operators + - * / in C++</td><td><r>F</r></td></tr><tr><td>We cannot use <k>malloc()</k> anymore in C++</td><td><r>F</r></td></tr><tr><td><k>int **ptr;</k> ptr is a pointer of pointer to integer</td><td><t>T</t></td></tr><tr><td><k>int arr[10];</k> arr is a pointer to integer</td><td><t>T</t></td></tr><tr><td><k>List *lp;</k> calls the List constructor (only <k>List l;</k> and <k>new List</k> do)</td><td><r>F</r></td></tr></table>''')
P1.append(sec('2. Linked List (Singly), full code'))
P1.append(fig(list_svg(), 'Node = _item + _next; last node\'s _next == NULL (loop stops here). Nodes live on the heap, need not be contiguous. insertHead(78), insertHead(551), insertHead(123) gives 123&rarr;551&rarr;78 (reverse of insertion order).'))
P1.append(code(S['list']))

P1.append('''<table><tr><th>SLL operation</th><th>time</th><th>why</th></tr>
<tr><td>insertHead / removeHead</td><td><b>O(1)</b></td><td>touch only head + new node, "regardless of size"</td></tr>
<tr><td>insertTail</td><td>O(1) with <k>_tail</k>; O(n) without</td><td>must walk to the end otherwise</td></tr>
<tr><td>removeTail</td><td><r>O(n)</r></td><td>need 2nd-last node; no prev pointer (DLL makes it O(1))</td></tr>
<tr><td>search / get(i) / searchMin</td><td>O(n)</td><td>only sequential access; <r>no binary search on a list</r></td></tr></table><ul><li><b>insertHead</b>: link new&rarr;old head <b>before</b> moving head. <b>removeHead</b>: temp=head &rarr; head=head-&gt;next &rarr; delete temp (PollEv order B,C,A); check empty first.</li><li><k>friend class List;</k> is written inside <k>ListNode</k>. Array: fixed size, O(1) random access. List: grows at run time, O(1) head insert, O(n) access. Doubly linked list adds <k>_prev</k> &rArr; removeTail O(1) (needed for Deque).</li></ul>''')

P1.append(sec('3. ADT, Stack, Queue'))
P1.append('<p><b>ADT</b> = specification only: <b>interface</b> + <b>behaviour</b>; <r>no implementation details</r> (algorithm + state). "ADT is the detailed implementation": <r>F</r>; "no implementation needed to define an ADT": <t>T</t>. Same interface, many implementations (Symbol table via list / hash table / tree; "arrays only is most efficient": <r>F</r>). Key = unique id for search/delete.</p>')
P1.append('''<table><tr><th>ADT</th><th>order</th><th>interface</th><th>linked-list impl.</th><th>array impl.</th></tr>
<tr><td><b>Stack</b></td><td><r>LIFO</r></td><td>push(x), pop() removes+returns most recent, empty()</td><td>top = head: push/pop <b>O(1)</b></td><td>top = end: push/pop O(1) if no overflow (fixed capacity)</td></tr>
<tr><td><b>Queue</b></td><td><r>FIFO</r></td><td>enqueue(x) at back, dequeue() removes+returns front, empty()</td><td>back = tail (needs <k>_tail</k>), front = head: both <b>O(1)</b></td><td>circular array O(1)</td></tr></table>''')
P1.append(code(S['stackq']))
P1.append('<p>Empty-stack pop: throw exception (postponed) or <b>modify the spec</b>: add <k>empty()</k>, caller checks first. "best push O(1), pop O(n)": <r>F</r>. Stack via augmented tree keyed by insertion order: <t>T</t>.</p>')
P1.append(code(S['stacksort']))

P1.append(sec('5. Searching &amp; Divide-and-Conquer'))
P1.append('<p><b>Linear search</b> (unsorted array / list): O(n) worst, O(1) best; global max/min of unsorted data: O(n) unavoidable. <b>Binary search</b> needs a <r>sorted array with random access</r> (not a list): after d halvings n/2ᵈ items remain; stop at 1 &rArr; d = log&#8322;n &rArr; <b>O(log n)</b>.</p>')
P1.append(code(S['bsearch']))
P1.append(code(S['badge']))
P1.append(code(S['peak']))
P1.append('''<ul>
<li><b>Peak finding</b> (local max; ends = &minus;&infin;): recurse into the <b>bigger</b> side, it must contain a peak (values can&#39;t rise forever); the smaller side may have none. Finding <i>all</i> peaks: &Omega;(n).</li>
<li><b>2D peak</b> (m cols &times; n rows): column global max + 1D peak = O(mn), correct but slow; column <i>local</i> max = wrong; <b>lazy evaluation</b> (column max computed only when visited) = <b>O(n log m)</b>.</li>
<li><b>Max profit</b> (buy once, sell later): one pass keeping min-so-far, O(n).</li>
<li><b>Russian dolls (2024 Oct)</b>: lowers sorted &rArr; binary search each upper, O(n log n); both unsorted &rArr; quicksort-style partition, expected O(n log n).</li></ul>''')
P1.append(sec('4a. Big O worked examples (rules &amp; tables: &sect;4 overleaf)'))
P1.append('''<table><tr><th class="m">code</th><th>Steps</th></tr>

<tr><td class="m">return n&lt;1 ? 1 : f(n*90.0/100.0);</td><td>Step 1: T(n)=T(0.9n)+1.<br>Step 2: after d calls size n&middot;0.9ᵈ; stops when =1.<br>Step 3: d = log&#8321;&#8320;&#8725;&#8329;n<br><b>&rArr; O(log n)</b><br><i>Note:</i> base is a constant &rArr; any f(0.9n) / f(0.7n) / f(n/3) is O(log n); never compute the base.</td></tr>
<tr><td class="m">if(n&lt;=1)return 0; doSomething(n);
return f(n/2)+f(n/2);</td><td>Step 1: T(n)=2T(n/2)+n.<br>Step 2: level d has 2ᵈ calls of size n/2ᵈ &rArr; cost n per level.<br>Step 3: log n levels<br><b>&rArr; O(n log n)</b></td></tr><tr><td class="m">for(i=0;i&lt;n;i++) O(1);
return f(n/2);
// ONE call only</td><td>Step 1: T(n)=T(n/2)+n.<br>Step 2: level d has 1 call of size n/2ᵈ &rArr; cost n/2ᵈ per level.<br>Step 3: n+n/2+n/4+&hellip; &le; 2n (geometric, r&lt;1 &rArr; &le; 2&times;first term).<br><b>&rArr; O(n)</b> (contrast: f(n/2)+f(n/2) gives n per level &rArr; O(n log n); &ldquo;叫一次不能乘&rdquo;)</td></tr>
<tr><td class="m">if(n&lt;=1)return 0;
return f(n-1)+f(n-1);
// no loop</td><td>Step 1: T(n)=2T(n&minus;1)+1.<br>Step 2: level d has 2ᵈ calls, each O(1) &rArr; cost 2ᵈ per level.<br>Step 3: n levels (size shrinks by 1) &rArr; 1+2+4+&hellip;+2ⁿ &le; 2&middot;2ⁿ.<br><b>&rArr; O(2ⁿ)</b> (naive Fibonacci shape)</td></tr>






<tr><td class="m">for(i=1;i&lt;n;i*=2)
 for(j=0;j&lt;n;j+=i)
  for(k=0;k&lt;j;k++) count++;</td><td>Step 1: i = 1,2,4,&hellip;,n (log n values).<br>Step 2: for fixed i, j = 0,i,2i,&hellip; (n/i values), inner cost j.<br>Step 3: &Sigma;j = i(0+1+&hellip;+n/i) &asymp; n&sup2;/(2i).<br>Step 4: &Sigma; over i of n&sup2;/i = n&sup2;(1+&frac12;+&frac14;+&hellip;) &le; 2n&sup2;<br><b>&rArr; O(n&sup2;)</b> (2025 Sep Q5)</td></tr>
</table>''')


P1.append(fig(rec_svg(), 'Recursion tree of T(n)=2T(n/2)+cn: every level costs cn, there are log&#8322;n levels &rArr; O(n log n).'))

# ---------------- PAGE 2 ----------------
P2 = []
P2.append(sec('4. Big O &amp; Time Complexity (Part A: 6&times;3 marks)'))
P2.append('''<p><b>Def:</b> T(n) = O(f(n)) iff &exist; c, n&#8320; with T(n) &le; c&middot;f(n) &forall; n &ge; n&#8320; (upper bound; c absorbs constants, n&#8320; skips the transient start). <b>&Omega;</b>: T(n) &ge; c&middot;f(n). <b>&Theta;</b>: both. Count operations, not seconds. <r>Answer the tightest bound</r>: 1000n is O(n); yet "an O(n&sup2;) algorithm is also O(n&sup3;) if not tight" <r>T</r>. n&sup3; is O(n&sup3;), &Omega;(n&sup2;), not &Theta;(n&sup2;). 1 &lt; log n &lt; n &lt; n log n &lt; n&sup2; &lt; n&sup3; &lt; 2&#8319; &lt; n!.</p>''')
P2.append('''<p><b>Rules:</b> sequential blocks add &rArr; <b>max</b>; nested loops/calls <b>multiply</b>; drop constants &amp; lower terms; if/else &rArr; costlier branch; log base irrelevant. <b>Sums:</b> 1+2+&hellip;+n = n(n+1)/2 = <r>O(n&sup2;)</r> (the loop computing it is O(n)); &Sigma;i&sup2; = O(n&sup3;); n+n/2+n/4+&hellip; &le; 2n = <r>O(n)</r>; 1+2+4+&hellip;+n &le; 2n; 1+&frac12;+&frac14;+&hellip; &le; 2; 1+&frac12;+&#8531;+&hellip;+1/n = O(log n); log(n!) = &Theta;(n log n); log(8n&sup2;+4n) = O(log n); 4n&sup2;log n + 8n = O(n&sup2;log n) (keep the log).</p>''')
P2.append(sub('Loop patterns (iterations &times; cost of one iteration)'))
P2.append('''<table><tr><th class="m">loop header</th><th>iterations</th><th>note</th></tr>
<tr><td class="m">for (i=0; i&lt;n; i++)  or n/4..2n, i&lt;=n</td><td>O(n)</td><td>i+=2, i&lt;n/3, i&lt;(n&sup2;+n)/3 &rArr; n/2, n/3, n&sup2;</td></tr>
<tr><td class="m">for (i=0; i&lt;n*n; i+=n)  or i+=2n</td><td>n&sup2;/n = O(n)</td><td>i=-n..n&sup2; step n &rArr; n+1</td></tr>
<tr><td class="m">for (i=1; i&lt;n; i*=2)  or n=n/2</td><td><r>O(log n)</r></td><td>i&lt;2n &rArr; log n + 1; i&lt;n&sup2; &rArr; 2 log n</td></tr>
<tr><td class="m">for (k=n/2,i=k+1; i&lt;n; i+=k,k/=2)</td><td>O(log n)</td><td>i &rarr; n/2+n/4+&hellip; needs log n adds</td></tr>
<tr><td class="m">for (j=0; j&lt;100; j++)  or j&lt;4; j*=2</td><td>O(1)</td><td>bound independent of n &rArr; constant</td></tr>
<tr><td class="m">for (i&lt;n) for (j&lt;n)  or j&lt;n/2, j&lt;2n</td><td>O(n&sup2;)</td><td>3 nested &rArr; O(n&sup3;) = "None"; inner j&lt;i &rArr; &Sigma;i = O(n&sup2;)</td></tr>
<tr><td class="m">for (i&lt;n) doSomething(i) [cost O(i)]</td><td>&Sigma;i = O(n&sup2;)</td><td>doSomething(n) inside n&times;n loops &rArr; n&sup3;</td></tr>

<tr><td class="m">while (rand()%n) ...</td><td>exp. O(n)</td><td>stop prob 1/n per round &rArr; E = n rounds</td></tr>
<tr><td class="m">for (i=0; i&lt;n; i*=2)</td><td>never ends</td><td>0*2 = 0 unless the body changes i (2024 Feb Q5)</td></tr></table>''')
P2.append(sub('How to judge a recursion'))
P2.append('''<p>Step 1: work of <b>one call</b> via the loop rules ("loop n" below = placeholder). Inner loop bounded by m independent of n &rArr; factor it out, multiply at the end (fixed number like 100 &rArr; drop).<br>
Step 2: <b>calls</b> per level and <b>levels</b>: &divide;k &rArr; log n levels; &minus;k &rArr; n levels.<br>
Step 3: cost of each level, then add the levels: <y>same every level &rArr; multiply by #levels; different &rArr; sum the series</y>.<br>
Step 4 (&ge;2 calls): add the <b>subproblem sizes</b>: = n &rArr; n per level &times; levels; &lt; n &rArr; shrinking, O(first term); &gt; n &rArr; <y>last level dominates</y> (4&times; f(n/2) &rArr; 4^(log&#8322;n) = n&sup2;).</p>
<table><colgroup><col style="width:26%"><col style="width:6%"><col style="width:8%"><col style="width:14%"><col style="width:46%"></colgroup><tr><th class="m">code</th><th>calls</th><th>levels</th><th>per level</th><th>answer</th></tr>
<tr><td class="m">f(n/k)</td><td>1</td><td>log n</td><td>1, 1, 1</td><td><b>O(log n)</b></td></tr>
<tr><td class="m">f(n&minus;k)</td><td>1</td><td>n</td><td>1, 1, 1</td><td><b>O(n)</b></td></tr>
<tr><td class="m">loop n; f(n/k)</td><td>1</td><td>log n</td><td>n, n/k, n/k&sup2;</td><td><b>O(n)</b> (<y><r>NOT n log n</r>: levels shrink, can&#39;t multiply</y>)</td></tr>
<tr><td class="m">loop n; f(n&minus;k)</td><td>1</td><td>n</td><td>n, n&minus;k, n&minus;2k</td><td><b>O(n&sup2;)</b></td></tr>
<tr><td class="m">loop n; k calls f(n/k)</td><td>k</td><td>log n</td><td>n, n, n</td><td><b>O(n log n)</b> (only if the subproblems add up to n)</td></tr>
<tr><td class="m">loop n²; f(n/2)+f(n/2)</td><td>2</td><td>log n</td><td>n², n²/2, n²/4</td><td><b>O(n²)</b> (<y>&frac12; size &rArr; &frac14; work, only 2&times; calls &rArr; each level halves</y>; geometric &le; 2n², <r>NOT n² log n</r>)</td></tr>
<tr><td class="m">f(n&minus;1)+f(n&minus;1)</td><td>2</td><td>n</td><td>1, 2, 4</td><td><b>O(2ⁿ)</b></td></tr>
<tr><td class="m">f(n&minus;k)+f(n&minus;m)</td><td>2</td><td>n</td><td>&le; doubles</td><td>exponential, write <b>O(2ⁿ)</b></td></tr>
<tr><td class="m">f(n&minus;1)+f(n&minus;2) (Fibonacci)</td><td>2</td><td>n</td><td>&le; doubles</td><td>exactly O(1.618ⁿ); in the quiz write <b>O(2ⁿ)</b></td></tr></table>
<p><b>Rules of thumb:</b> subtract a constant + 1 call = O(n); subtract a constant + &ge;2 calls = exponential; divide by a constant + k calls = n log n. <b>Special:</b> <r>return inside the loop &rArr; loop runs once. No base case &rArr; None of the above.</r></p>''')
P2.append(sub('Recurrences not in the table above'))
P2.append('''<table><tr><th>recurrence (code shape)</th><th>answer</th><th>Steps</th></tr>





<tr><td>T(n)=T(n/10)+T(9n/10)+cn &nbsp;<span class="tiny">(quicksort 1:9; not covered by k calls f(n/k))</span></td><td><r>O(n log n)</r></td><td><y>unequal split, but sizes still add up to n &rArr; n per level</y>; depth = longest path log&#8321;&#8320;&#8725;&#8329; n</td></tr>
<tr><td>T(n)=10T(n/10)+cn &nbsp;<span class="tiny">(loop n, then 10 calls f(n/10))</span></td><td><r>O(n log n)</r></td><td>10&middot;(n/10) = n per level, log&#8321;&#8320;n levels</td></tr><tr><td>T(n)=2T(n&minus;1)+c <span class="tiny">(naive Fibonacci)</span> / f(10) inside f(n) / <b>no base case</b></td><td><r>O(2ⁿ)</r> / O(1) / <r>None</r></td><td>doubles per level &times; n levels / constant-size call / never ends</td></tr>
</table>''')
P2.append(sec('6. Sorting (Bubble / Selection / Insertion / Merge / Quick)'))
P2.append('''<table><colgroup><col style="width:8%"><col style="width:11%"><col style="width:9%"><col style="width:11%"><col style="width:10%"><col style="width:7%"><col style="width:44%"></colgroup><tr><th>sort</th><th>best</th><th>avg</th><th>worst</th><th>extra mem</th><th>stable</th><th>after pass i (detective clue)</th></tr>
<tr><td><b>Bubble</b></td><td>n (early stop, sorted input)</td><td>n&sup2;</td><td>n&sup2;</td><td>O(1) in-place</td><td><r>Yes</r></td><td>largest i at <b>right end</b> (final); rest moved by adjacent swaps only</td></tr>
<tr><td><b>Selection</b></td><td><r>n&sup2;</r></td><td>n&sup2;</td><td>n&sup2;</td><td>O(1)</td><td><r>No</r>*</td><td>smallest i at <b>left end</b> (final); rest in original order</td></tr>
<tr><td><b>Insertion</b></td><td>n (already ascending)</td><td>n&sup2;</td><td>n&sup2; (descending)</td><td>O(1)</td><td>Yes</td><td>left i+1 items <b>sorted, not final</b>; right untouched</td></tr>
<tr><td><b>Merge</b></td><td>n log n</td><td>n log n</td><td>n log n</td><td><r>O(n)</r> not in-place</td><td>Yes (left on tie)</td><td>sorted runs of length 2,4,8&hellip;; nothing crosses halves early</td></tr>
<tr><td><b>Quick</b></td><td>n log n</td><td>n log n (expected)</td><td><r>n&sup2;</r> (sorted, fixed pivot)</td><td>in-place; stack O(log n)</td><td>No</td><td>pivot final; all left &le; pivot &lt; all right (grouped, not ordered)</td></tr></table>''')
P2.append('<p class="tiny">*stable with O(n) extra space. Cocktail sort = two-way <b>Bubble</b> (not Merge), O(n&sup2;). Any <b>comparison sort</b> is &Omega;(n log n): decision tree has n! leaves &rArr; height &ge; log&#8322;(n!) = &Theta;(n log n); merge sort meets it. Needs a transitive ordering (rock-paper-scissors unsortable).</p>')
P2.append('<p><b>Detective (2022):</b> 6 3 1 4 8 7 5 2 &rarr; <k>1 2 3 4 8 7 5 6</k> Selection (left 4 final, rest untouched); <k>3 1 4 6 5 2 7 8</k> Bubble (7,8 at right); <k>1 3 6 4 8 7 5 2</k> Insertion (left 3 sorted, right untouched); <k>1 3 4 6 2 5 7 8</k> Merge (two sorted halves); <k>3 1 4 2 5 6 8 7</k> Quick (5 in place, left&lt;5&lt;right). <b>2024 Feb:</b> 14 12 40 6 8 100 7 109 &rarr; 6 8 7 12 14 40 100 109 = <b>Quick</b> (pivot 12). <b>Code:</b> <k>for i: for j=i+1: if A[i]&gt;A[j] swap</k> = Selection; <k>if A[i]&gt;A[n-1] swap; sort(A,n-1)</k> = Selection; adjacent <k>A[j]&gt;A[j+1]</k> = Bubble; shift with <k>key</k> = Insertion.</p>')
P2.append(code(S['bubble'])); P2.append(code(S['selection'])); P2.append(code(S['insertion']))
P2.append(code(S['merge']))

P2.append(code(S['quick']))
P2.append(code('''
partition, pivot=22:  22 35 10 42 7 51 18  -> swap 35,18: 22 18 10 42 7 51 35
 -> swap 42,7: 22 18 10 7 42 51 35 -> hands cross, swap pivot with A[high]
 -> 7 18 10 [22] 42 51 35   "which was the pivot?" = left all <= it < right
    e.g. 18 5 6 1 10 22 40 32 50 -> 22 or 50 (50: its right side is empty)
merge trace (2022): 37 11 21 56 14 18 97 3 -> singles
 -> [11 37][21 56][14 18][3 97] -> [11 21 37 56][3 14 18 97] -> sorted''', 'pl'))
P2.append('''<p><b>QuickSort analysis</b></p><ul>
<li>T(n) = O(n) + T(p) + T(n&minus;1&minus;p). Middle pivot every time &rArr; 2T(n/2)+n = <b>O(n log n)</b>.</li>
<li>Min/max pivot every time (fixed first/last pivot on <r>sorted / almost sorted input</r>) &rArr; T(n&minus;1)+n = <r>O(n&sup2;)</r>. Unsorted input can still hit n&sup2; ("never n&sup2; if not sorted": <r>F</r>).</li>
<li><b>Random pivot</b>: <i>good</i> = both sides &gt; n/10. P(good) = 8/10 &rArr; expected 1/p = 1.25 (&le;2) tries &rArr; <b>expected O(n log n) for every input</b>; worst case still n&sup2;.</li>
<li>Any constant split (1:9, 2:8) works: depth log&#8321;&#8320;&#8725;&#8329;n &times; n per level. Exact median: P = 1/n &rArr; n tries &rArr; n&sup2;. "expected n log n if each side has size &ge; 10": <r>F</r> (must be a constant <i>fraction</i>).</li>
<li>Randomized (algorithm flips coins, any input) &ne; average case (input assumed random). In-place: <t>T</t>. Needs O(log n) call stack: <t>T</t>. Not stable. Sorts a linked list in O(n log n): <t>T</t>.</li>
<li>Duplicates: use &le; on one side or 3-way partition (&lt;x | =x | &gt;x), else infinite loop.</li>
<li>Merge sort on a linked list is still O(n log n) ("slower on lists": <r>F</r>, "O(n&sup2;)": <r>F</r>). Merge sort caches poorly ("best caching": <r>F</r>). Insertion sort is still used for small / nearly sorted input ("nobody uses it": <r>F</r>).</li></ul>''')
P2.append(sec('7. Binary Trees &amp; BST (all functions, O(h))'))
P2.append('<p><b>Binary tree</b>: each node &le; 2 children. <b>BST</b>: for <b>every</b> node v, all keys in left subtree &lt; v &lt; all keys in right subtree (whole subtrees, not just the 2 children; in-order strictly increasing). <b>Balanced BST</b> (AVL, not in quiz) adds a height rule. <b>Height</b>: <r>leaf = 0, empty = &minus;1</r>, node = 1 + max(child heights). Height h &rArr; &ge; h+1 nodes (chain), &le; 2^(h+1)&minus;1 ("at least 2^h&minus;1": <r>F</r>). n nodes &rArr; h from &lfloor;log&#8322;n&rfloor; to <r>n&minus;1</r> (sorted inserts; "height can be n": <r>F</r>); shape depends on insertion order.</p>')
P2.append(fig(tree_svg(), 'Lecture tree. in-order: 11 20 29 32 41 50 65 72 91 99 (sorted!) &middot; pre-order: 41 20 11 29 32 65 50 91 72 99 &middot; post-order: 11 32 29 20 50 72 99 91 65 41 &middot; level-order: 41 20 65 11 29 50 91 32 72 99'))
P2.append(code(S['tree']))
P2.append(fig(delete_svg(), 'Successor of a 2-child node has no left child &rArr; &le;1 child &rArr; 2nd delete is case 0/1: delete is O(h), <b>not</b> O(n).'))
P2.append(code(S['treeops']))
P2.append(code(S['traverse']))
P2.append('''<p><b>Complexity</b></p><ul>
<li>search / insert / delete / min / max / successor / predecessor = <r>O(h)</r>: one root-to-leaf path. h = O(log n) only if balanced, O(n) worst ("all BSTs give O(log n) search": <r>F</r>).</li>
<li>Any traversal = <r>O(n)</r> ("in-order is O(n log n)": <r>F</r>). Building by n inserts = O(n&middot;h), n&sup2; for sorted input.</li>
<li>Sorted array: search O(log n) but insert O(n). Linked list: insert O(1) but search O(n). BST: everything O(h).</li></ul>
<p><b>Successor &amp; traversal facts</b></p><ul>
<li><b>Successor(x)</b>: (1) x has a right subtree &rArr; its min; (2) else the lowest ancestor where the search <b>turned left</b>; none &rArr; x is max. Works if x is absent: succ(33)=41. succ(20)=29, succ(11)=20, succ(32)=41. Predecessor mirrors.</li>
<li>In-order of a <b>BST</b> = ascending. In-order of an arbitrary binary tree is sorted: <r>F</r>.</li>
<li>Pre-order is "never sorted": <r>F</r> (right chain 1&rarr;2&rarr;3). Post-order of a BST is "always not sorted": <r>F</r> (left chain 3&larr;2&larr;1 gives 1 2 3). Pre-order = reverse of post-order: <r>F</r>.</li>
<li>Min = leftmost node, <r>not necessarily a leaf</r>. Level order = BFS with a queue. Pre-order: copy tree / expression tree; post-order: delete tree.</li>
<li>Insert always creates a <b>leaf</b>. Recursive insert / delete <b>return</b> the subtree root and the caller catches it.</li>
<li><b>Order statistics</b> (k-th smallest, dynamic): store each node&#39;s subtree <b>size</b>, not its rank ("store the rank": <r>F</r>, one insert changes every larger rank). select(k): r = size(left)+1; k=r &rArr; me; k&lt;r &rArr; left; k&gt;r &rArr; right with k&minus;r.</li></ul>''')


PAGES = [P1, P2]
