from keras.datasets import reuters
from keras import layers
from keras import models
from keras import optimizers
from keras import losses
from keras import metrics
import matplotlib.pyplot as plt
import numpy as np

def print_array(inArray, position = 0, initText = "???"):
	text = initText + " >>> "
	for x in inArray[position]:
		text += " " + "{}".format(x)
	return text

def to_one_hot(labels, dimension = 46):
	results = np.zeros((len(labels), dimension))
	for i, label in enumerate(labels):
		results[i, label] = 1.
	return results

def vectorize_sequences(sequences, dimension=10000):
	results = np.zeros((len(sequences), dimension))
	for i, sequence in enumerate(sequences):
		results[i, sequence] = 1.
	return results

# save np.load
np_load_old = np.load

# modify the default parameters of np.load
np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)

# call load_data with allow_pickle implicitly set to true
(train_data, train_labels), (test_data, test_labels) = reuters.load_data(num_words=10000)

# restore np.load for future normal usage
np.load = np_load_old

# labels = ""
# for x in train_labels:
# 	labels += "{}".format(x)
# print (labels)
print(train_labels)

word_index = reuters.get_word_index()
reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

# #print(reverse_word_index)
decoded_review = [reverse_word_index.get(i-3, '???') for i in train_data[1800]]
#print(decoded_review)

x_train = vectorize_sequences(train_data)
x_test = vectorize_sequences(test_data)

one_hot_train_labels = to_one_hot(train_labels)
one_hot_test_labels = to_one_hot(test_labels)

print(one_hot_train_labels)

modelPath = r"C:\_WORK\PYTHON\projects\keras\multiclass_classification_example-results\myModel.HDF5"

# y_train = np.asarray(train_labels).astype("float32")
# y_test = np.asarray(test_labels).astype("float32")

# print("y_test[0:50] >>> {0}".format(y_test[0:50]))
# print("y_train[0:50] >>> {0}".format(y_train[0:50]))

inputText = "Do you want to load or fit the network ? - Load(l) / Fit(f)\n"
myInput = input(inputText)
if myInput == "l" or myInput == "L" or myInput == "Load" or myInput == "LOAD":
	myModel = models.load_model(modelPath)
	print(dir(myModel))
	model = models.Sequential()
	model.load_weights(modelPath)
	
else:
	model = models.Sequential()
	model.add(layers.Dense(64, activation="relu", input_shape=(10000,)))
	model.add(layers.Dense(64, activation="relu"))
	model.add(layers.Dense(46, activation="softmax"))
	model.compile(optimizer="rmsprop", loss="categorical_crossentropy", metrics=["accuracy"])
	#model.compile(optimizer=optimizers.RMSprop(lr=0.001), loss=losses.binary_crossentropy , metrics=[metrics.binary_accuracy])

	x_val = x_train[:1000]
	partial_x_train = x_train[1000:]
	y_val = one_hot_train_labels[:1000]
	partial_y_train = one_hot_train_labels[1000:]

	# print("x_val[0:50] >>> {0}".format(x_val[0:50]))
	# print("partial_x_train >>> {0}".format(partial_x_train))
	epochs_num = 9
	history = model.fit(partial_x_train, \
						partial_y_train, \
						epochs=epochs_num, \
						batch_size=512, \
						validation_data=(x_val,y_val))
	results = model.evaluate(x_test, one_hot_test_labels)
	print("final results: {}".format(results))
	model.save(modelPath)

history_dict = history.history
print(history_dict.keys())

# #printing the training and validation loss
loss_values = history_dict["loss"]
val_loss_values = history_dict["val_loss"]
epochs = range(1, len(loss_values) + 1)
plt.plot(epochs, loss_values, "bo", label="Training loss")
plt.plot(epochs, val_loss_values, "b", label="Validation loss")
plt.title("Training and validation loss")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.show()

# #inputText = "Do you want to display training and validation accuracy ? - Yes(y) / No(n)\n"
# #myInput = input(inputText)
# #printing the training and validaytion accuracy
# # if myInput == "y" or myInput == "Y" or myInput == "yes" or myInput == "YES":
# # 	plt.clf()
# # 	acc_values = history_dict["binary_accuracy"]
# # 	val_acc_values = history_dict["val_binary_accuracy"]
# # 	plt.plot(epochs, acc_values, "bo", label="Training acc")
# # 	plt.plot(epochs, val_acc_values, "b", label="Validation acc")
# # 	plt.title("Training and validation accuracy")
# # 	plt.xlabel("Epochs")
# # 	plt.ylabel("Loss")
# # 	plt.legend()
# # 	plt.show()

plt.clf()
acc_values = history_dict["acc"]
val_acc_values = history_dict["val_acc"]
plt.plot(epochs, acc_values, "bo", label="Training acc")
plt.plot(epochs, val_acc_values, "b", label="Validation acc")
plt.title("Training and validation accuracy")
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.legend()
plt.show()
prediction = model.predict(x_test)
predictedLabelIndexes = [np.argmax(x) for x in prediction]
predicatedAccuracy = np.amax(prediction, axis=1)
print("predicatedAccuracy >>> {}".format(predicatedAccuracy))
#predictions = np.argmax(model.predict(x_test))
plt.clf()
#print("len(predictions): {0} - {1}".format(len(predictedLabelIndexes), predictedLabelIndexes))
predictions_range = range(1, len(predictedLabelIndexes) + 1)
plt.plot(predictions_range, predictedLabelIndexes, "bo", label="Topic index")
plt.title("Prediction of topic label index")
plt.xlabel("Prediction samples")
plt.ylabel("Index of topic")
plt.legend()
plt.show()

plt.clf()
#print("len(predictions): {0} - {1}".format(len(predictedLabelIndexes), predictedLabelIndexes))
predictions_range = range(1, predicatedAccuracy.shape[0] + 1)
plt.plot(predictions_range, predicatedAccuracy, "bo", label="Accuracy sample")
plt.title("Prediction accuracy of most likely topic index")
plt.xlabel("Prediction samples")
plt.ylabel("Accuracy")
plt.legend()
plt.show()