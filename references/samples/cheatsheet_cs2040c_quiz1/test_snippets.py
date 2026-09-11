from snippets import S
import re
def clean(s):
    return '\n'.join(re.sub(r'^!! |^!R ', '', l) for l in s.strip('\n').split('\n'))
parts = ['#include <iostream>\n#include <queue>\n#include <algorithm>\n#include <cstdlib>\n#include <climits>\nusing namespace std;\n']
cls = clean(S['class']).replace('BankAcct b;', 'void ctorTest() { BankAcct b;').replace('p = new BankAcct(50);   // constructor runs -> destructor only on: delete p;', 'p = new BankAcct(50); delete p; }')
parts.append('namespace A {\n' + clean(S['list']) + '\n' + clean(S['stackq']) + '\n' + cls + '\n}\n')
parts.append('namespace B {\n' + clean(S['list']) + '\n' + clean(S['inherit']).replace('Stack *s = new BeeBooStack();','void t(){ Stack *s = new BeeBooStack();').replace('BeeBooStack b; b.empty();','BeeBooStack b; b.empty(); delete s; }').replace('Animal *a = new Dog(); a->talk();', 'void t2() { Animal *a = new Dog();  a->talk(); delete a; }') + '\n}\n')
parts.append('namespace C {\n' + '\n'.join(clean(S[k]) for k in ['bsearch','badge','peak','bubble','selection','insertion','merge','quick']) + '\n}\n')
parts.append('namespace D {\n' + '\n'.join(clean(S[k]) for k in ['tree','treeops','traverse']) + '\n}\n')
ptr = clean(S['ptr']).replace('int *a = new int[n];','int n=3; int *a = new int[n];')
pas = clean(S['pass'])
# split pass: function defs vs statements
pdefs = '\n'.join(l for l in pas.split('\n') if l.startswith('void') or l.startswith('int max') or l.startswith('//'))
pdefs = pdefs.replace('int max(int a, int b);  int max(int a, int b, int c);  double max(double a, double b);','int mx(int a, int b){return a>b?a:b;}  int mx(int a, int b, int c){return mx(mx(a,b),c);}  double mx(double a, double b){return a>b?a:b;}')
pstm = '\n'.join(l for l in pas.split('\n') if l.startswith('int x1') or l.startswith('cout'))
parts.append('namespace E {\n' + pdefs + '\nvoid run(){\n' + pstm + '\n' + ptr + '\n}\n}\n')
# stacksort test
parts.append('''
struct LL { A::List l; bool empty(){return l.empty();} int head(){return l.headItem();} void push_head(int x){l.insertHead(x);} int pop_head(){int t=l.headItem(); l.removeHead(); return t;} };
void stacksort(LL &L1, LL &L2){ int temp;
''' + '\n'.join(l for l in clean(S['stacksort']).split('\n') if not l.startswith('//')) + '\n}\n')
parts.append(r'''
int main(){
  E::run(); cout << endl;
  A::List l; l.insertHead(78); l.insertHead(551); l.insertHead(123); l.insertTail(9);
  cout << l.searchMin() << " " << " "; l.reverse(); 
  while(!l.empty()){ cout << l.headItem() << " "; l.removeHead(); } cout << endl;
  A::Stack st; st.push(1); st.push(2); cout << st.pop() << st.pop() << " "; cout << endl;
  A::BankAcct ba(100); cout << ba.withdraw(50) << ba.withdraw(500) << endl;
  B::t();
  LL L1, L2; int v[]={5,1,4,2,3}; for(int x: v) L1.push_head(x); stacksort(L1,L2); while(!L2.empty()) cout << L2.pop_head() << " "; cout << endl;
  srand(1);
  for(int trial=0; trial<3000; trial++){ int n = rand()%30+1; int base[40]; for(int i=0;i<n;i++) base[i]=rand()%10;
    int a[5][40]; for(int s=0;s<5;s++) copy(base, base+n, a[s]);
    C::bubbleSort(a[0],n); C::selectionSort(a[1],n); C::insertionSort(a[2],n); C::mergeSort(a[3],0,n-1); C::quickSort(a[4],0,n-1);
    sort(base, base+n); for(int s=0;s<5;s++) for(int i=0;i<n;i++) if(a[s][i]!=base[i]){ cout << "SORT FAIL " << s << endl; return 1; }
    for(int i=0;i<n;i++){ int idx=C::binarySearch(base,n,base[i]); if(base[idx]!=base[i]){cout<<"BS FAIL"<<endl; return 1;} }
    if(C::binarySearch(base,n,11)!=-1){cout<<"BS FAIL2"<<endl; return 1;}
    // badge
    int m = rand()%20+2; int miss = rand()%m+1; int arr[40], k=0; for(int x=1;x<=m;x++) if(x!=miss) arr[k++]=x; if(C::missingBadge(arr,m)!=miss){cout<<"BADGE FAIL "<<m<<" "<<miss<<endl; return 1;}
    // peak
    int p = C::peak1D(base,0,n-1); if((p>0 && base[p-1]>base[p])||(p<n-1&&base[p+1]>base[p])){cout<<"PEAK FAIL"<<endl; return 1;}
  }
  D::BinarySearchTree<int> t; int keys[]={41,20,65,11,29,50,91,32,72,99}; for(int x: keys) t.insert(x);
  t.inOrder(); cout << "| "; t.levelOrder(); cout << "| h=" << t.height() << " min " << t.searchMin() << endl;
  cout << "succ " << t.successor(20) << t.successor(11) << " " << t.successor(32) << " " << t.successor(33) << " " << t.successor(99) << " " << t.exist(72) << t.exist(73) << endl;
  t.remove(65); t.inOrder(); cout << "| "; t.levelOrder(); cout << endl; t.remove(29); t.remove(11); t.inOrder(); cout << endl;
  return 0;
}
''')
open('test.cpp','w').write('\n'.join(parts))
