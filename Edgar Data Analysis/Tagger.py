#Import required libraries
import csv
import pprint
from collections import defaultdict
import  os
import numpy as np
from sklearn.utils import check_random_state
import os

from os import environ
from os.path import dirname
from os.path import join
from os.path import exists
from os.path import expanduser
from os.path import isdir
from os.path import splitext
from os import listdir
from os import makedirs


def load_files(container_path, description=None, categories=None,
               load_content=True, shuffle=True, encoding=None,
               decode_error='strict', random_state=0):
    target = []
    target_names = []
    filenames = []

    folders = [f for f in sorted(listdir(container_path))
               if isdir(join(container_path, f))]

    if categories is not None:
        folders = [f for f in folders if f in categories]

    for label, folder in enumerate(folders):
        target_names.append(folder)
        folder_path = join(container_path, folder)
        documents = [join(folder_path, d)
                     for d in sorted(listdir(folder_path))]
        target.extend(len(documents) * [label])
        filenames.extend(documents)

    # convert to array for fancy indexing
    filenames = np.array(filenames)
    target = np.array(target)

    if shuffle:
        random_state = check_random_state(random_state)
        indices = np.arange(filenames.shape[0])
        random_state.shuffle(indices)
        filenames = filenames[indices]
        target = target[indices]

    if load_content:
        data = []
        for filename in filenames:
            with open(filename, 'rb') as f:
                data.append(f.read())
        if encoding is not None:
            data = [d.decode(encoding, decode_error) for d in data]
        return Bunch(data=data,
                     filenames=filenames,
                     target_names=target_names,
                     target=target,
                     DESCR=description)

    return Bunch(filenames=filenames,
                 target_names=target_names,
                 target=target,
                 DESCR=description)

class Bunch(dict):
    """Container object for datasets
    Dictionary-like object that exposes its keys as attributes.
    >>> b = Bunch(a=1, b=2)
    >>> b['b']
    2
    >>> b.b
    2
    >>> b.a = 3
    >>> b['a']
    3
    >>> b.c = 6
    >>> b['c']
    6
    """

    def __init__(self, **kwargs):
        super(Bunch, self).__init__(kwargs)

    def __setattr__(self, key, value):
        self[key] = value

    def __dir__(self):
        return self.keys()

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setstate__(self, state):
        # Bunch pickles generated with scikit-learn 0.16.* have an non
        # empty __dict__. This causes a surprising behaviour when
        # loading these pickles scikit-learn 0.17: reading bunch.key
        # uses __dict__ but assigning to bunch.key use __setattr__ and
        # only changes bunch['key']. More details can be found at:
        # https://github.com/scikit-learn/scikit-learn/issues/6196.
        # Overriding __setstate__ to be a noop has the effect of
        # ignoring the pickled __dict__
        pass

# Creating category-wise folders for storring training dataset into textual format  
def create_dataset_folder(parent_folder, riskTrainSet):
    if not os.path.exists(parent_folder):
        os.makedirs(parent_folder)
    os.chdir(parent_folder)

    folders = riskTrainSet.keys()

    for label, folder in enumerate(folders):
        if not os.path.exists(folder):
            os.makedirs(folder)
        os.chdir(folder)

        count = 0

        for d in sorted(riskTrainSet[folder]):
            fp = open(str(str(folder) + "_" + str(count) + ".txt"), "w", encoding="utf-8")
            fp.write(str(d[1]))
            fp.close()
            count += 1
        os.chdir("..")

    os.chdir("..")

def crearteDataset(riskTrainSet, description, shuffle=True, random_state=0):
    target = []
    target_names = []
    filenames = []
    data = []

    folders = riskTrainSet.keys()

    for label, folder in enumerate(folders):
        # print(label, folder)
        for d in sorted(riskTrainSet[folder]):
            data.append(d[1])

        target_names.append(folder)
        documents = [d[0] for d in sorted(riskTrainSet[folder])]
        target.extend(len(documents) * [label])
        filenames.extend(documents)

    # convert to array for fancy indexing
    filenames = np.array(filenames)
    target = np.array(target)

    if shuffle:
        random_state = check_random_state(random_state)
        indices = np.arange(filenames.shape[0])
        random_state.shuffle(indices)
        filenames = filenames[indices]
        target = target[indices]

    return Bunch(data=data,
                filenames=filenames,
                target_names=target_names,
                target=target,
                DESCR=description)

def classifier(riskTrainSet, riskTestSet):

	# Below code is used to create the textual files for training and testing data set into 
	# category-wise folder
    # twenty_train = crearteDataset(riskTrainSet, "", shuffle=True, random_state=42)
    # twenty_test = crearteDataset(riskTestSet, "", shuffle=True, random_state=42)

    # create_dataset_folder("Train",riskTrainSet)
    # create_dataset_folder("Test",riskTestSet)
	
    categ = riskTrainSet.keys()
    twenty_train = load_files("Train", categories=categ, shuffle=True, random_state=42)
    docs_test = load_files("Test", categories=categ, shuffle=True, random_state=42)

    from sklearn.feature_extraction.text import CountVectorizer
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(twenty_train.data)

    from sklearn.feature_extraction.text import TfidfTransformer
    tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
    X_train_tf = tf_transformer.transform(X_train_counts)

    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

    from sklearn.naive_bayes import MultinomialNB
    clf = MultinomialNB().fit(X_train_tfidf, twenty_train.target)

	# Manual test data to test the classifier
    docs_new = ['We depend substantially on the successful completion of Phase 3 clinical trials for our product candidates. The positive clinical results obtained for our product candidates in Phase 2 clinical studies may not be repeated in Phase 3.',
                'We face potential liability related to the privacy of health information we obtain from research institutions.',
                'Our patents and other proprietary rights may fail to protect our business. If we are unable to adequately protect our intellectual property; third parties may be able to use our technology which could adversely affect our ability to compete in the market.',
                'Even if our drug candidates obtain regulatory approval; we and our collaborators will be subject to ongoing government regulation.']
    X_new_counts = count_vect.transform(docs_new)
    X_new_tfidf = tfidf_transformer.transform(X_new_counts)

    predicted = clf.predict(X_new_tfidf)
    print("\n********************* Prediction of Manual Test Data *********************\n")
    for doc, category in zip(docs_new, predicted):
        print('%r => %s' % (doc[:100], twenty_train.target_names[category]))

	# Calculating accuracy, precision, confusion matrix using test data set
    print("\n********************* Prediction of Test Data Set *********************\n")
    from sklearn.pipeline import Pipeline
    text_clf = Pipeline([('vect', CountVectorizer()),

                         ('tfidf', TfidfTransformer()),

                         ('clf', MultinomialNB()),

                         ])

    text_clf = text_clf.fit(twenty_train.data, twenty_train.target)

    test = docs_test.data
    predicted = text_clf.predict(test)
    for doc, category in zip(test, predicted):
        print('%r => %s' % (doc[:100], twenty_train.target_names[category]))

    print("\n********************* Evaluation of Classification Algorithm *********************")

    print("\nOverall Accuracy of Test Data Set:", np.mean(predicted == docs_test.target))

    from sklearn import metrics
    print("\nClassification Report:\n")
    print(metrics.classification_report(docs_test.target, predicted, target_names=docs_test.target_names))
    print("\nConfusion Matrix:\n")
    print(metrics.confusion_matrix(docs_test.target, predicted))


riskTestSet = defaultdict(list)

riskTrainSet = defaultdict(list)

path = "C:\\Users\\Capstone\\Desktop\\Files to Categorize\\Tagged\\"

testCreated = False

for file in  os.listdir(path):

    #reading CSV file to read the tagged data
    with open(path + file , 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')

        ind = -1
        for line in lines:
            ind += 1
            if(ind == 0):
                continue

            CIK = line[0]
            Company_Name = line[1]
            Date = line[2]
            Form_Type = line[3]

            if(ind == 2):
                break

        for line in lines:
            Risk_Factor_Bold_Tags = line[4]
            Risk_Factor_Paragraphs = line[5]
            Notes = line[6]
            Category_for_Risk_Factor = line[7]
            Business_Bold_Tags = line[8]
            Business_Paragraphs = line[9]
            Category_for_Business = line[10]

            # Storing bold and paragraphs text of each category.
            for Category in str(Category_for_Risk_Factor).split(","):
                Category = Category.strip()
                if Category is not '':
                    if not testCreated:
                        riskTestSet[Category].append([Risk_Factor_Bold_Tags, Risk_Factor_Paragraphs])
                        riskTrainSet[Category].append([Risk_Factor_Bold_Tags, Risk_Factor_Paragraphs])
                    else:
                        riskTrainSet[Category].append([Risk_Factor_Bold_Tags, Risk_Factor_Paragraphs])

    testCreated = True

# Function Call
classifier(riskTrainSet, riskTestSet)

