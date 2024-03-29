import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("./mnist/data/", one_hot=True)

# Hyper parameter
total_epoch = 500
batch_size = 100
learning_rate = 0.0001


n_hidden = 256
n_input = 28 * 28
n_noise = 128

X = tf.placeholder(tf.float32, [None, n_input])
Z = tf.placeholder(tf.float32, [None, n_noise])

def generator(noise_z) :
    with tf.variable_scope('generator') :
        hidden = tf.layers.dense(inputs=noise_z, units=n_hidden, activation=tf.nn.relu)
        output = tf.layers.dense(inputs=hidden, units=n_input, activation=tf.nn.sigmoid)

    return output

def discriminator(inputs, reuse=None) :
    with tf.variable_scope('discriminator') as scope:
        if reuse :
            scope.reuse_variables()
        hidden = tf.layers.dense(inputs=inputs, units=n_hidden, activation=tf.nn.relu)
        output = tf.layers.dense(inputs=hidden, units=1, activation=tf.nn.sigmoid)
    return output

def get_noise(batch_size, n_noise) :
    return np.random.normal(size=(batch_size, n_noise))

G = generator(Z)
D_real = discriminator(X)
D_gene = discriminator(G, reuse=True)

loss_D = tf.reduce_mean(tf.log(D_real) + tf.log(1 - D_gene))
tf.summary.scalar('loss_D', -loss_D)
loss_G = tf.reduce_mean(tf.log(D_gene))
tf.summary.scalar('loss_G', -loss_G)

vars_D = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope='discriminator')
vars_G = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope='generator')

train_D = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(-loss_D, var_list=vars_D)
train_G = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(-loss_G, var_list=vars_G)

with tf.Session() as sess :
    sess.run(tf.global_variables_initializer())

    total_batch = int(mnist.train.num_examples/batch_size)
    loss_val_D, loss_val_G = 0, 0

    merged = tf.summary.merge_all()
    writer = tf.summary.FileWriter('./logs_epoch500_batch100', sess.graph)

    for epoch in range(total_epoch) :
        for i in range(total_batch) :
            batch_x, batch_y = mnist.train.next_batch(batch_size)
            noise = get_noise(batch_size, n_noise)
            _, loss_val_D = sess.run([train_D, loss_D],
                                     feed_dict={X : batch_x, Z : noise})
            _, loss_val_G = sess.run([train_G, loss_G],
                                     feed_dict={Z : noise})
        summary = sess.run(merged, feed_dict={X: batch_x, Z: noise})
        writer.add_summary(summary, global_step=epoch)

        print('Epoch:', '%04d' % epoch,
              'D loss: {:.4}'.format(-loss_val_D),
              'G loss: {:.4}'.format(-loss_val_G))
        if epoch == 0 or epoch % 10 == 0 or epoch == total_epoch-1:
            sample_size = 10
            noise = get_noise(sample_size, n_noise)
            samples = sess.run(G,
                               feed_dict={Z : noise})

            fig, ax = plt.subplots(nrows=1, ncols=sample_size, figsize=(sample_size, 1))

            for i in range(sample_size) :
                ax[i].set_axis_off()
                ax[i].imshow(np.reshape(samples[i], (28,28)))

            plt.savefig('samples_epoch500_batch100/{}.png'.format(str(epoch).zfill(3)), bbox_inches='tight')
            plt.close(fig)

    print('Optimized!')
