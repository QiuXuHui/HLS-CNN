"""CNN weights generator

This program uses a CNN model built with Tensorflow/Keras to compute
the weights that will be used by the C/HLS network.

Produces a set of header files as output: definitions.h, conv_weights.h,
dense_weights.h.

images size: 28x28

"""

from os import path
from turtle import shape
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import ZeroPadding2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.optimizers import SGD
from sklearn.model_selection import KFold
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
from numpy import mean
from numpy import size
from numpy import std
from numpy import empty
from matplotlib import pyplot as plt


# Constants.
input_size			= (28,28)
conv_1_kernel_size 	= (3,3)
conv_1_filter_num 	= 4
pool_1_size 		= (2,2)
dense_1_size		= 100
dense_2_size		= 10


def load_dataset():
	# Load dataset.
	(trainX, trainY), (testX, testY) = mnist.load_data()
	# Reshape dataset to have a single channel.
	trainX = trainX.reshape((trainX.shape[0], input_size[0], input_size[1], 1))
	testX = testX.reshape((testX.shape[0], input_size[0], input_size[1], 1))
	# One hot encode target values.
	trainY = to_categorical(trainY)
	testY = to_categorical(testY)
	return trainX, trainY, testX, testY

def prep_pixels(train, test):
	# Convert from integers to floats.
	train_norm = train.astype('float32')
	test_norm = test.astype('float32')
	# Normalize to range 0-1.
	train_norm = train_norm / 255.0
	test_norm = test_norm / 255.0
	# Return normalized images.
	return train_norm, test_norm

def define_model() -> Sequential:
	# Define model.
	model = Sequential()
	model.add(ZeroPadding2D(padding=1, input_shape=(input_size[0], input_size[1], 1)))
	model.add(Conv2D(conv_1_filter_num, conv_1_kernel_size, activation='relu', padding='valid', kernel_initializer='he_uniform', input_shape=(30, 30, 1)))
	#model.add(BatchNormalization())
	model.add(MaxPooling2D(pool_1_size))
	model.add(Flatten())
	#model.add(Dense(100, activation='relu', kernel_initializer='he_uniform'))
	#model.add(BatchNormalization())
	model.add(Dense(10, activation='softmax'))
	# Compile model.
	opt = SGD(learning_rate=0.01, momentum=0.9)
	model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
	return model

def gen_conv_params(layer:Conv2D,
		label:str, kr:str, kc:str, f:str) -> str:
	'''
	Takes a Conv2D layer as input and returns a C initialization (as a
	string) of '(label)_weights[kr][kc][f]' and '(label)_biases[f]'
	arrays.
	'''

	w, b = layer.weights
	res = ''

	# Conversion of weights array.
	new_w = empty(shape=(w.shape[3],w.shape[0],w.shape[1]))
	for row in range(w.shape[0]):
		for col in range(w.shape[1]):
			for filter in range(w.shape[3]):
				new_w[filter][row][col] = w[row][col][0][filter]
	w = new_w

	# Weights: (label)_weights[kr][kc][f].
	res += '// ' + label.capitalize() + ' layer weights.\n'
	res += 'float ' + label + '_weights [' + f + '][' + kr + '][' \
			+ kc + ']\n\t= {\n'
	for filter in range(w.shape[0]):
		res += '\t\t\t{\n'
		for row in range(w.shape[1]):
			res += '\t\t\t\t{ '
			for col in range(w.shape[2]):
				res += str(float(w[filter][row][col]))
				if (col != w.shape[2]-1):
					res += ', '
			res += ' }'
			if(row != w.shape[1] -1):
				res += ','
			res += '\n'
		res += '\t\t\t}'
		if(filter != w.shape[0] -1):
			res += ','
		res += '\n'
	res +='\t\t};\n\n'

	# Biases: (label)_biases[f].
	res += '// ' + label.capitalize() + ' layer biases.\n'
	res += 'float ' + label + '_biases [' + f + '] = { '
	for i in range(b.shape[0]):
		res += str(float(b[i]))
		if (i != b.shape[0]-1):
			res += ', '
	res += ' };'

	return res

def gen_dense_params(layer:Dense, label:str, size0: str, size1: str):
	'''
	Takes a Dense layer as input and returns a C initialization (as a
	string) of '(label)_weights[size0][size1]' and '(label)_biases[size1]'
	arrays.
	'''

	w, b = layer.weights
	res = ''

	# Conversion of weights array.
	pool_img_r = int(input_size[0]/pool_1_size[0])
	pool_img_c = int(input_size[1]/pool_1_size[1])

	tmp = empty(shape=(pool_img_r, pool_img_c, conv_1_filter_num, dense_2_size))
	index = 0
	for i in range(pool_img_r):
		for j in range(pool_img_c):
			for f in range(conv_1_filter_num):
				for d in range(dense_2_size):
					tmp[i][j][f][d] = w[index][d]
				index += 1
	index = 0
	new_w = empty(w.shape)
	for f in range(conv_1_filter_num):
		for i in range(pool_img_r):
			for j in range(pool_img_c):
				for d in range(dense_2_size):
					new_w[index][d] = tmp[i][j][f][d]
				index += 1
	w = new_w

	# Weights: (label)_weights[size0][size1].
	res += '// ' + label.capitalize() + ' layer weights.\n'
	res += 'float ' + label + '_weights[' + size0 + '][' + size1 + ']\n\t = {\n'
	for i in range(w.shape[0]):
		res += '\t\t\t{ '
		for j in range(w.shape[1]):
			res += str(float(w[i][j]))
			if j != w.shape[1] - 1:
				res += ', '
		res += ' }'
		if i != w.shape[0] - 1:
			res += ','
		res += '\n'
	res += '\t\t};\n\n'

	# Biases : (label)_biases[size1].
	res += '// ' + label.capitalize() + ' layer biases.\n'
	res += 'float ' + label + '_biases [' + size1 + '] = { '
	for i in range(b.shape[0]):
		res += str(float(b[i]))
		if (i != b.shape[0]-1):
			res += ', '
	res += ' };'

	return res

def save_param_on_files(model: Sequential) -> None:
	'''
	Saves model constants and layers parameter of the sequential
	model 'model'.
	Writes on 'definitions.h', 'conv_weights.h' ,'dense_weights.h' files.
	'''

	# definitions.h
	with open('../C/definitions.h', 'w') as f:
		print('writing \'definitions.h\' file... ', end='')
		print('/*\n * This file is auto-generated by gen-weights.py\n */\n',file=f)
		print('#pragma once', file=f)
		print('\n#include <stdint.h>\n\n#define DIGITS 10\n\n#define IMG_ROWS '
			+str(input_size[0])+'\n#define IMG_COLS '+str(input_size[1])+'\n',file=f)
		# padding
		print('// Padding.',file=f)
		print( ''
			+ '#define	PAD_ROWS (KRN_ROWS - 1)\n'
			+ '#define	PAD_COLS (KRN_COLS - 1)\n'
			+ '#define PAD_IMG_ROWS (IMG_ROWS + PAD_ROWS)\n'
			+ '#define PAD_IMG_COLS (IMG_COLS + PAD_COLS)\n'
			, file=f)
		# conv_1 constant
		print('// Convolutional layer.',file=f)
		print('#define KRN_ROWS\t',end='',file=f)
		print(conv_1_kernel_size[0], file=f)
		print('#define KRN_COLS\t',end='',file=f)
		print(conv_1_kernel_size[1], file=f)
		print('#define FILTERS\t',end='',file=f)
		print(conv_1_filter_num, file=f, end='\n\n')
		# pool
		print('// Pool layer.\n'
			+ '#define POOL_ROWS\t' + str(pool_1_size[0]) + '\n'
			+ '#define POOL_COLS\t' + str(pool_1_size[1]) + '\n'
			+ '#define POOL_IMG_ROWS (IMG_ROWS / POOL_ROWS)\n'
			+ '#define POOL_IMG_COLS (IMG_COLS / POOL_COLS)\n'
			, file=f)
		# flatten
		print('// Fatten layer.\n'
			+ '#define FLAT_SIZE (FILTERS * POOL_IMG_ROWS * POOL_IMG_COLS)\n'
			, file=f)
		# dense
		print('// Dense layers.\n'
			#+ '#define DENSE1_SIZE ' + str(dense_1_size) + '\n'
			+ '#define DENSE_SIZE ' + str(dense_2_size)
			, file=f
		)
		print('done.')

	# conv_weights.h
	conv_layer = model.layers[1]
	assert(isinstance(conv_layer, Conv2D))

	with open('../C/conv_weights.h', 'w') as f:
		print('writing \'conv_weights.h\' file... ', end='')
		print('/*\n * This file is auto-generated by gen-weights.py\n */\n',file=f)
		print('#pragma once\n\n#include "definitions.h"\n\n',file=f)
		arrays_def_str = gen_conv_params(conv_layer, 'conv',
			'KRN_ROWS', 'KRN_COLS', 'FILTERS')
		print(arrays_def_str, file=f)
		print('done.')

	# dense_weights.h
	#dense1_layer = model.layers[4]
	#assert(isinstance(dense1_layer, Dense))
	#dense2_layer = model.layers[5]
	dense2_layer = model.layers[4]
	assert(isinstance(dense2_layer, Dense))

	with open('../C/dense_weights.h', 'w') as f:
		print('writing \'dense_weights.h\' file... ', end='')
		print('/*\n * This file is auto-generated by gen-weights.py\n */\n',file=f)
		print('#pragma once\n\n#include "definitions.h"\n\n', file=f)
		# dense 1
		#arrays_def_str = gen_dense_params(dense1_layer, 'dense1',
		#	'FLAT_SIZE', 'DENSE1_SIZE')
		#print(arrays_def_str, file=f)
		#print(file=f)
		# dense 2
		arrays_def_str = gen_dense_params(dense2_layer, 'dense',
			'FLAT_SIZE', 'DENSE_SIZE')
		print(arrays_def_str, file=f)
		print('done.')

def main() -> None:

    # Load dataset.
	trainX, trainY, testX, testY = load_dataset()
	print('trainX.shape = ', trainX.shape)
	print('trainY.shape = ', trainY.shape)
	print('testX.shape = ', testX.shape)
	print('testY.shape = ', testY.shape)
	# Normalize input images.
	trainX, testX = prep_pixels(trainX, testX)

	# If a trained model is already available: load it.
	# Else: define a new model, train and save it.
	if not path.isfile('model.h5'):
		print('model not found: create and train it')
		model = define_model()
		history = model.fit(trainX, trainY, epochs=20, batch_size=32, validation_data=(testX, testY), verbose=1)
		model.save("model.h5")
		print('model saved as \'model.h5\'')
	else:
		print('found a model: use it.')
		model = load_model('model.h5')

	# Print summary.
	print(model.summary())
	# Evaluate model.
	_, acc = model.evaluate(testX, testY, verbose=0)
	print('Accuracy: %.3f' % (acc * 100.0))

	# Save parameters and weights on header files.
	save_param_on_files(model)

	# --- SOME OLD STUFF ---

	# inference on one image
	#print(testX.shape)
	#image = testX[1]
	#print(image.shape)
	#image = np.array(image, dtype='float')
	#pixels = image.reshape((28, 28))
	#plt.imshow(pixels, cmap='gray')
	#plt.title(testY[1])
	#plt.show()
	#pred = model.fit(image)
	#print(pred)
	#res = np.array(model.predict(testX[1]))
	#res = res.transpose()

	#for i in range(res.shape[0]):
	#	print('---')
	#	for j in range(res.shape[2]):
	#		for k in range(res.shape[3]):
	#			print(int(res[i][0][k][j]), end='')
	#		print()

    # train
#    scores, histories = evaluate_model(trainX,trainY)
#
#	from keras.models import Model
#	layer_name = 'conv2d'
#	intermediate_layer_model = Model(inputs=model.input,
#                                 outputs=model.get_layer(layer_name).output)
#	intermediate_output = intermediate_layer_model.predict(testX[1])
#	print(intermediate_output.shape)
#
#	w = intermediate_output
#	new_w = np.empty(shape=(w.shape[3],w.shape[0],w.shape[1]))
#
#	for r in range(w.shape[0]):
#		for c in range(w.shape[1]):
#			for f in range(w.shape[3]):
#				new_w[f][r][c] = w[r][c][0][f]
#				#new_w[f][c][r] = w[r][c][0][f]


	#intermediate_output = intermediate_output.transpose()[0][0]
	#print(intermediate_output.shape)
#	for i in range(new_w.shape[0]):
#		print('---')
#		for j in range(new_w.shape[1]): # row
#			for k in range(new_w.shape[2]): # col
#				print(int(round(new_w[i][j][k],6)), end=' ')
#			print()
#


if __name__ == '__main__':
	main()





#
# Functions from original article, not used yet.
# https://machinelearningmastery.com/how-to-develop-a-convolutional-neural-network-from-scratch-for-mnist-handwritten-digit-classification/
#


# evaluate a model using k-fold cross-validation
#def evaluate_model(dataX, dataY, n_folds=5):
#	scores, histories = list(), list()
#	# prepare cross validation
#	kfold = KFold(n_folds, shuffle=True, random_state=1)
#	# enumerate splits
#	for train_ix, test_ix in kfold.split(dataX):
#		# define model
#		model = define_model()
#		# select rows for train and test
#		trainX, trainY, testX, testY = dataX[train_ix], dataY[train_ix], dataX[test_ix], dataY[test_ix]
#		# fit model
#		history = model.fit(trainX, trainY, epochs=3, batch_size=32, validation_data=(testX, testY), verbose=0)
#		# evaluate model
#		_, acc = model.evaluate(testX, testY, verbose=0)
#		print('> %.3f' % (acc * 100.0))
#		# stores scores
#		scores.append(acc)
#		histories.append(history)
#	return model, scores, histories


# plot diagnostic learning curves
#def summarize_diagnostics(histories):
#	for i in range(len(histories)):
#		# plot loss
#		plt.subplot(2, 1, 1)
#		plt.title('Cross Entropy Loss')
#		plt.plot(histories[i].history['loss'], color='blue', label='train')
#		plt.plot(histories[i].history['val_loss'], color='orange', label='test')
#		# plot accuracy
#		plt.subplot(2, 1, 2)
#		plt.title('Classification Accuracy')
#		plt.plot(histories[i].history['accuracy'], color='blue', label='train')
#		plt.plot(histories[i].history['val_accuracy'], color='orange', label='test')
#	plt.show()

# summarize model performance
#def summarize_performance(scores):
#	# print summary
#	print('Accuracy: mean=%.3f std=%.3f, n=%d' % (mean(scores)*100, std(scores)*100, len(scores)))
#	# box and whisker plots of results
#	plt.boxplot(scores)
#	plt.show()
