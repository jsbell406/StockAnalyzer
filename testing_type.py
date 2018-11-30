from datetime import datetime

if __name__ == "__main__":

    # Doesn't work
    
    array = [1,2,3,4,5]

    total_score = 0

    [total_score = total_score + num for num in array]

    print(total_score)