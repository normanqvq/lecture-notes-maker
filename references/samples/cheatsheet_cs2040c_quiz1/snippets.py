S = {}

S['ptr'] = r'''
int x = 5;  int *p = &x;   // p stores the ADDRESS of x  (& = address-of)
*p = 7;                    // *p = "go to that address": x is now 7 (dereference)
int **pp = &p;             // pointer to pointer  (quiz: "int **ptr is ptr-to-ptr" T)
int arr[10];               // arr acts as a pointer to arr[0]  (quiz: T)
int *q = new int;          // heap memory: no name, reachable ONLY via q
delete q;  q = NULL; // q is DANGLING after delete -> set NULL, never reuse
int *a = new int[n];  delete [] a;   // dynamic array needs delete []
'''

S['pass'] = r'''
void f1(int a)  { a = 10; }   // pass by VALUE: a is a copy, x1 stays 1
void f2(int &a) { a = 10; }   // pass by REFERENCE: a IS x2 (alias, not a ptr)
void f3(int *a) { *a = 10; }  // pass by POINTER: a holds &x3
!! f1(x1); f2(x2); f3(&x3);  cout << x1 << x2 << x3;   // 1 10 10
int max(int a, int b);  double max(double a, double b);  // overloading:
                                    // same name, different signature
'''

S['class'] = r'''
class BankAcct { // members are PRIVATE by default (struct: public)
private:
    int _acc_num;  double _balance;   // attributes: members + friends only
public:
    BankAcct() { _balance = 0; } // constructor: same name, NO return type
    BankAcct(double b) { _balance = b; } // >1 constructor OK; may be private
    ~BankAcct() { }                       // destructor: ONLY ONE, no params
    int withdraw(double amt);             // declare here, define outside:
    friend class Auditor;   // Auditor may read my private/protected members
};
int BankAcct::withdraw(double amt) {      // Class:: scope
    if (_balance < amt) return 0;
    _balance -= amt;  return 1;
}
'''

S['inherit'] = r'''
class Stack {                  // parent / base / superclass
protected:  List _ll; // private: child CANNOT access; protected: child can
public:
    virtual void push(int x) { _ll.insertHead(x); } // virtual: polymorphism
    virtual int pop() { int t = _ll.headItem(); _ll.removeHead(); return t; }
    bool empty() { return _ll.empty(); }
};
class BeeBooStack : public Stack { // child / derived / subclass, is-a Stack
public:
    void push(int x) { cout << "Bee" << endl; Stack::push(x); }  // OVERRIDE
!!     int pop() { cout << "Boo" << endl; return Stack::pop(); }  // Stack::!
};
Stack *s = new BeeBooStack(); s->push(1); // "Bee" (virtual) else Stack::push
BeeBooStack b; b.empty(); // inherited: child has ALL functionality of parent
class Animal { public: virtual void talk() { cout << "*Nothing*"; } };
class Dog : public Animal { public: void talk() { cout << "Woof"; } };
Animal *a = new Dog(); a->talk(); // Woof (virtual). No virtual -> *Nothing*
'''

S['list'] = r'''
class ListNode {
private:
    int _item;
    ListNode *_next;
public:
    ListNode(int x) { _item = x; _next = NULL; }
    friend class List;        // List may touch _item/_next (one-way!)
};
class List {
private:
    int _size;
    ListNode *_head;
    ListNode *_tail;          // extra: makes insertTail O(1)
public:
    List() { _size = 0; _head = NULL; _tail = NULL; }
    ~List() { while (_size > 0) removeHead(); }   // free every node (no GC)
    bool empty() { return _size == 0; }
    int headItem() { return _head->_item; } // caller checks !empty() first
    void insertHead(int x);  void insertTail(int x);   void removeHead();
    bool exist(int x);  int searchMin();  void reverse();  // removeTail: O(n)
};

void List::insertHead(int x) {                 // O(1) regardless of size
    ListNode *aNewNode = new ListNode(x);      // 1. create node
!!     aNewNode->_next = _head; // 2. new -> old head (MUST be before 3)
!!     _head = aNewNode;                          // 3. head -> new
    if (_size == 0) _tail = aNewNode;          //    empty -> non-empty: tail
    _size++;                                   // 4.
}   //! swap 2 and 3: old list lost (leak) + node points to itself

void List::insertTail(int x) { // O(1) with _tail; O(n) if walking to end
    ListNode *aNewNode = new ListNode(x);
    if (_size == 0) _head = aNewNode; // empty: new node is also the head
    else _tail->_next = aNewNode;              // old tail links forward
    _tail = aNewNode;  _size++;
}

void List::removeHead() {
    if (_size == 0) return; // handle empty (NULL->_next crashes)
!!     ListNode *temp = _head;                    // 1. remember old head
!!     _head = _head->_next;                      // 2. move head
!!     delete temp; // 3. free it (else ORPHAN = leak)
    _size--;                                   // 4.
    if (_size == 0) _tail = NULL;              //    non-empty -> empty
}



bool List::exist(int x) {                      // linear search O(n); NO binary search here
    for (ListNode *cur = _head; cur != NULL; cur = cur->_next)
        if (cur->_item == x) return true;
    return false;
}

int List::searchMin() { // 2023 Sep Part D (list non-empty)
    ListNode *current = _head;
    int minimum = _head->_item;
    while (current) {
        if (minimum > current->_item) minimum = current->_item;
        current = current->_next;
    }
    return minimum;
}

void List::reverse() {                   // O(n) time, O(1) space (PE favourite)
    ListNode *prev = NULL, *cur = _head;
    _tail = _head;                       // old head becomes the tail
    while (cur) {
        ListNode *nxt = cur->_next;      // save next BEFORE breaking the link
        cur->_next = prev;               // flip the pointer
        prev = cur;  cur = nxt;          // advance
    }
    _head = prev;                        // last node is the new head
}
'''

S['stackq'] = r'''
class Stack { // LIFO. composition: wraps a List, hides the rest
private:  List _ll;
public:
    void push(int x) { _ll.insertHead(x); } // O(1)
    int pop() { int t = _ll.headItem(); _ll.removeHead(); return t; } // O(1)
    bool empty() { return _ll.empty(); } // spec: caller checks before pop()
};
// Queue: same wrapper. enqueue(x) = _ll.insertTail(x)   (back = tail, O(1))
//                      dequeue()  = headItem + removeHead  (front = head)
//! never dequeue at the tail: SLL removeTail is O(n)
'''

S['stacksort'] = r'''
// 2025 Sep Part C: L1 -> L2 ascending; only head/empty/push_head/pop_head
while (!L1.empty()) {
    temp = L1.pop_head();
    while (!L2.empty() && L2.head() < temp)   // keep L2 ascending from head:
        L1.push_head(L2.pop_head()); //   smaller ones go back to L1 for now
    L2.push_head(temp);
}   // = insertion sort with 2 stacks: O(n^2)
'''

S['bsearch'] = r'''
int binarySearch(int A[], int n, int key) {   // A SORTED. O(log n)
    int lo = 0, hi = n - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (A[mid] == key) return mid;
        else if (key < A[mid]) hi = mid - 1;  // smaller: drop right half
        else lo = mid + 1;                    // bigger: drop left half
    }
    return -1;                                // range empty -> not found
}
'''

S['badge'] = r'''
int missingBadge(int A[], int n) { // A sorted, has n-1 of 1..n (2025 Feb).
    int lo = 0, hi = n - 2;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (A[mid] == mid + 1) lo = mid + 1; // A[0..mid] in place: gap right
        else hi = mid - 1; // gap already before mid -> go left
    }
    return lo + 1;
}
'''

S['peak'] = r'''
int peak1D(int A[], int lo, int hi) { // index of ANY local max. O(log n)
    int mid = (lo + hi) / 2;
    if (mid > lo && A[mid-1] > A[mid]) return peak1D(A, lo, mid-1); // bigger
    if (mid < hi && A[mid+1] > A[mid]) return peak1D(A, mid+1, hi); //  side
    return mid;                               // >= both neighbours: peak
}
'''

S['bubble'] = r'''
void bubbleSort(int A[], int n) { // swaps NEIGHBOURS. stable, in-place
    for (int i = 0; i < n - 1; i++) { // pass i: max of A[0..n-1-i] -> right
        bool swapped = false;
        for (int j = 0; j < n - 1 - i; j++)
            if (A[j] > A[j+1]) { swap(A[j], A[j+1]); swapped = true; }
        if (!swapped) break; // early stop: best O(n); worst still O(n^2)
    }
}
'''
S['selection'] = r'''
void selectionSort(int A[], int n) { // ALWAYS O(n^2). NOT stable
    for (int i = 0; i < n - 1; i++) {
        int minIdx = i;
        for (int j = i + 1; j < n; j++)    // scan unsorted part for min
            if (A[j] < A[minIdx]) minIdx = j;
        swap(A[i], A[minIdx]); // ONE far swap per pass -> unstable
    }
}
'''
S['insertion'] = r'''
void insertionSort(int A[], int n) { // worst O(n^2), best O(n)
    for (int j = 1; j < n; j++) { // stable, in-place; good if nearly sorted
        int key = A[j], i = j - 1;         // pick next card
        while (i >= 0 && A[i] > key) { A[i+1] = A[i]; i--; }  // shift right
        A[i+1] = key; // drop key into sorted part A[0..j-1]
    }
}
'''
S['merge'] = r'''
void merge(int A[], int lo, int mid, int hi) { // merge sorted
    int n = hi - lo + 1, *R = new int[n], i = lo, j = mid + 1, k = 0;
    while (i <= mid && j <= hi)
        R[k++] = (A[i] <= A[j]) ? A[i++] : A[j++]; // <= on tie: STABLE
    while (i <= mid) R[k++] = A[i++];             // leftovers
    while (j <= hi) R[k++] = A[j++];
    for (k = 0; k < n; k++) A[lo + k] = R[k];
    delete [] R; // O(n) EXTRA space -> not in-place
}
void mergeSort(int A[], int lo, int hi) { // T(n) = 2T(n/2)+cn = O(n log n)
    if (lo >= hi) return;                         // 1 element is sorted
    int mid = (lo + hi) / 2;
    mergeSort(A, lo, mid); // divide until single elements ...
    mergeSort(A, mid + 1, hi);
    merge(A, lo, mid, hi); // ... all the work is on the way back
}
'''
S['quick'] = r'''
int partition(int A[], int lo, int hi) {  // pivot = A[lo]. O(n)
    int pivot = A[lo], low = lo + 1, high = hi;
    while (low <= high) {
        while (low <= high && A[low] <= pivot) low++;   // left hand skips <=
        while (low <= high && A[high] > pivot) high--;  // right hand skips >
        if (low < high) swap(A[low], A[high]); // both stuck: swap (unstable)
    }
    swap(A[lo], A[high]); // pivot into place: left all <=, right all >
    return high;
}
void quickSort(int A[], int lo, int hi) { // work BEFORE recursing; no merge
    if (lo >= hi) return;
    // randomized: swap(A[lo], A[lo + rand()%(hi-lo+1)]) -> expected n log n
    int p = partition(A, lo, hi);          // T(n) = O(n) + T(p) + T(n-1-p)
    quickSort(A, lo, p - 1);  quickSort(A, p + 1, hi);
} // in-place (O(1) extra data) but recursion stack O(log n) avg, O(n) worst
'''

S['tree'] = r'''
template <class T> class BinarySearchTree;
template <class T>
class TreeNode {
private:  T _item;  TreeNode<T> *_left, *_right;   // ListNode + 2 nexts
public:   TreeNode(T x) { _item = x; _left = _right = NULL; }
          friend class BinarySearchTree<T>; // the tree may touch my privates
};

template <class T>
class BinarySearchTree {
private:
    TreeNode<T> *_root;   int _size;
    TreeNode<T>* _insert(TreeNode<T> *t, T x);
    TreeNode<T>* _remove(TreeNode<T> *t, T x);
    void _inOrder(TreeNode<T> *t);  int _height(TreeNode<T> *t);
public:
    BinarySearchTree() { _root = NULL; _size = 0; }  // dtor: post-order
    void insert(T x) { _root = _insert(_root, x); }  // catch returned root
    void remove(T x) { _root = _remove(_root, x); }
    void inOrder() { _inOrder(_root); }
    int height() { return _height(_root); }
    bool exist(T x);   T searchMin();   T successor(T x);   void levelOrder();
};
'''
S['treeops'] = r'''
template <class T>
bool BinarySearchTree<T>::exist(T x) { // search, O(h): one root-to-leaf path
    TreeNode<T> *cur = _root;
    while (cur) {
        if (x == cur->_item) return true;
        cur = (x < cur->_item) ? cur->_left : cur->_right;  // small L, big R
    }
    return false;                          // fell off (NULL): not in tree
}

template <class T>
T BinarySearchTree<T>::searchMin() { // 2023 Feb Part D: keep going LEFT
!!     TreeNode<T> *current = _root;
!!     while (current->_left) current = current->_left;
!!     return current->_item; // min = leftmost node (NOT always a leaf!)
}   // searchMax: same with _right

template <class T>
TreeNode<T>* BinarySearchTree<T>::_insert(TreeNode<T> *t, T x) {  // O(h)
    if (t == NULL) { _size++; return new TreeNode<T>(x); }  // new LEAF
    if (x < t->_item) t->_left = _insert(t->_left, x); // catch returned root
    else if (x > t->_item) t->_right = _insert(t->_right, x);
    return t; // (duplicate: ignored)
}

template <class T>
T BinarySearchTree<T>::successor(T x) {  // smallest item > x. O(h)
    TreeNode<T> *cur = _root, *lastLeft = NULL;
    while (cur && cur->_item != x) { // search for x ...
        if (x < cur->_item) { lastLeft = cur; cur = cur->_left; } // L
        else cur = cur->_right; // went right: cur < x, no
    }
    if (cur && cur->_right) { // case 1: min of right subtree
        cur = cur->_right;
        while (cur->_left) cur = cur->_left;
        return cur->_item;
    }
    if (lastLeft) return lastLeft->_item; // case 2: lowest ancestor
    return -1; // none: x is the max. predecessor = mirror image
}

template <class T>
TreeNode<T>* BinarySearchTree<T>::_remove(TreeNode<T> *t, T x) {  // O(h)
    if (t == NULL) return NULL;                       // not found
    if (x < t->_item) t->_left = _remove(t->_left, x);
    else if (x > t->_item) t->_right = _remove(t->_right, x);
    else {                                            // found t
        if (t->_left == NULL && t->_right == NULL) {   // case 0: leaf
            delete t; _size--; return NULL; }
        if (t->_left == NULL || t->_right == NULL) {   // case 1 child
            TreeNode<T> *child = t->_left ? t->_left : t->_right;
            delete t; _size--; return child; }
!!         TreeNode<T> *s = t->_right; // case 2 children: successor
!!         while (s->_left) s = s->_left;
!!         t->_item = s->_item; //   copy successor's item into t
!!         t->_right = _remove(t->_right, s->_item);  // delete successor
    }
    return t;
}
'''
S['traverse'] = r'''
template <class T>
void BinarySearchTree<T>::_inOrder(TreeNode<T> *t) { // O(n): every node once
    if (t == NULL) return;
    _inOrder(t->_left);                 // L
    cout << t->_item << " ";  // self (pre-order: FIRST; post-order: LAST)
    _inOrder(t->_right);                // R
}

template <class T>
void BinarySearchTree<T>::levelOrder() { // 2024 Feb Part D: BFS with a QUEUE
    if (_root == NULL) return;
    queue<TreeNode<T>*> q;  q.push(_root);
    while (!q.empty()) {
        TreeNode<T> *x = q.front(); q.pop();   // dequeue
        cout << x->_item << " ";               // process
        if (x->_left) q.push(x->_left);   // enqueue children, L then R
        if (x->_right) q.push(x->_right);
    }
}

template <class T>
int BinarySearchTree<T>::_height(TreeNode<T> *t) { // leaf = 0, empty = -1
    if (t == NULL) return -1;
    return max(_height(t->_left), _height(t->_right)) + 1;
}
'''
