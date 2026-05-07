# GoalLang Runtime Library
def goal_shout(*args):
    print(*(str(arg) for arg in args))

def goal_add(a, b):
    if isinstance(a, str) or isinstance(b, str):
        return str(a) + str(b)
    return a + b

def goal_receive():
    val = input()
    try:
        if '.' in val: return float(val)
        return int(val)
    except ValueError:
        return val

if __name__ == "__main__":
    goal_shout('=== GoalLang Test ===')
    goal_shout('Enter your name:')
    name = goal_receive()
    goal_shout('Enter number:')
    n = goal_receive()
    goal_shout(goal_add('Hello ', name))
    x = 0
    while (x < n):
        if ((x % 2) == 0):
            goal_shout(goal_add(x, ' even'))
        else:
            goal_shout(goal_add(x, ' odd'))
        x = goal_add(x, 1)
    goal_shout('Done!')