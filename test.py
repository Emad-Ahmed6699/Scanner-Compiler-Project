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

def main():
    goal_shout('Welcome to GoalLang!')
    goals = 5
    goal_shout(goal_add('Goals scored: ', goals))
    bonus = 2
    total = goal_add(goals, bonus)
    goal_shout(goal_add('Total Score with Bonus: ', total))
    if (total > 5):
        goal_shout('You are a Pro Player!')
    else:
        goal_shout('Keep training.')

if __name__ == "__main__":
    main()