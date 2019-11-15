left_list = [(0.0, 0.0), (1.1, 1.1), (2.2, 2.2)]
right_list = [(123.0, 234.0), (123.0, 234.0), (123.0, 234.0)]

def test():
    if len(left_list) < 2 or len(right_list) < 2:
        print "1"
    elif left_list == right_list:
        print "2"
    else:
        #print "3"
        flag1, flag2 = 0, 0
        len_list = len(left_list)
        #print len_list
        for i in range(len_list - 1):
            if left_list[i] == left_list[i + 1]:
                flag1 += 1
            if right_list[i] == right_list[i + 1]:
                flag2 += 1
        if flag1 == len_list -1 or flag2 == len_list -1:
            print "yes"
test()