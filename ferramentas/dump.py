import json,sys
d=json.load(open('/home/claude/build/questions.json'))
ex=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3])
for q in d['questions']:
    if q['exam']==ex and a<=q['num']<=b:
        print(f"### {q['id']} [{q['area']}] GAB={q['answer']}")
        if q.get('context'): print("CTX:", q['context'][:1500])
        print(q['stem'])
        for L,o in zip('ABCDE',q['options']): print(f"{L}) {o}")
        print()
