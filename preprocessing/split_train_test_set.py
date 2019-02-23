import csv
import random
import os


# Reads the csv data into a multi-dimensional array
def read_csv_data():
    with open(input_file, 'r') as input_stream:
        csv_reader = csv.reader(input_stream)
        return list(csv_reader)


# Writes the csv header and returns the writer object
def write_csv_data(target_file):
    test_data_file_path = os.path.join(output_directory, target_file)
    test_data = csv.writer(open(test_data_file_path, 'w'))
    test_data.writerow(['id', 'title', 'body'])
    return test_data


# Takes a sample of random post indices of all posts
def get_random_indices():
    indices_list = []
    for row_index, posts_row in enumerate(csv_data):
        if row_index > 0:
            indices_list.append(posts_row[0])
    return random.sample(indices_list, test_data_posts_count)


# Writes all randomly selected rows into the test data file
def write_test_data():
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    test_data = write_csv_data(test_data_file)

    test_row_count = 0
    while test_row_count < test_data_posts_count:  # Keep going till we got all test data posts
        for row_index, posts_row in enumerate(csv_data):
            if row_index > 0:
                if int(posts_row[0]) == int(random_indices[test_row_count]):  # Find the row with that random index
                    test_data.writerow(posts_row)
                    break
        test_row_count += 1
        # print(repr(float(test_row_count) / test_data_posts_count * 100) + " percent completed")


# Writes the remaining rows into the training data set
def write_train_data():
    train_data = write_csv_data(train_data_file)

    for row_index, posts_row in enumerate(csv_data):
        if row_index > 0:
            if not contains(random_indices, posts_row[0]):
                train_data.writerow(posts_row)


# Returns true if the element is contained in the list otherwise false
def contains(array_list, element):
    for list_element in array_list:
        if int(list_element) == int(element):
            return True
    return False


# Global configuration variables
input_file = 'unix.csv'
test_data_posts_count = 100
output_directory = 'output'
test_data_file = 'test.csv'
train_data_file = 'train.csv'

print('Reading input file...'),
csv_data = read_csv_data()
print('OK!')
print('Generating random indices...'),
random_indices = get_random_indices()
print('OK!')
print('Writing test data...'),
write_test_data()
print('OK!')
print('Writing train data...'),
write_train_data()
print('OK!')
