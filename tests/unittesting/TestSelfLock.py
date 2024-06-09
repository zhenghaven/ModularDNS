#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import unittest
import threading
import time

from ModularDNS.LockwSLD import LockwSLD, SelfLockError


class TestSelfLock(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def LockingThread(self, lock: LockwSLD, toRelease: threading.Event) -> None:
		with lock:
			while not toRelease.is_set():
				time.sleep(0.100) # 100ms

	def test_SelfLock_1Basics(self):
		lock = LockwSLD()
		self.assertFalse(lock.locked())
		self.assertEqual(lock.HeldBy(), None)
		self.assertFalse(lock.IsHeldByThisThread())

		releaseSignal = threading.Event()

		lockingThread = threading.Thread(
			target=self.LockingThread,
			args=(lock, releaseSignal)
		)
		lockingThread.start()

		# no blocking acquire
		self.assertFalse(lock.acquire(blocking=False))
		self.assertTrue(lock.locked())
		self.assertNotEqual(lock.HeldBy(), None)
		self.assertFalse(lock.IsHeldByThisThread())

		# blocking but with timeout
		startT = time.time()
		self.assertFalse(lock.acquire(blocking=True, timeout=0.200))
		endT = time.time()
		self.assertGreaterEqual(endT - startT, 0.200) # delta >= 200ms
		self.assertTrue(lock.locked())
		self.assertNotEqual(lock.HeldBy(), None)
		self.assertFalse(lock.IsHeldByThisThread())

		# clean up
		releaseSignal.set()
		lockingThread.join()

	def test_SelfLock_2SelfLockDetection(self):
		# the existing lock in python is not guaranteed that
		# when a thread holds the lock,
		# and when it tries to acquire the lock again,
		# it will throw an exception
		# so the following code will hang forever
		# lock = threading.Lock()
		# with lock as tmp:
		# 	print(type(tmp), tmp)
		# 	with lock:
		# 		pass

		lock = LockwSLD()
		self.assertFalse(lock.locked())
		self.assertEqual(lock.HeldBy(), None)

		with lock as ret:
			self.assertTrue(ret)
			self.assertTrue(lock.locked())
			self.assertEqual(lock.HeldBy(), threading.get_ident())
			self.assertTrue(lock.IsHeldByThisThread())

			with self.assertRaises(SelfLockError):
				with lock:
					pass

			# the lock should still be held by the current thread
			self.assertTrue(lock.locked())
			self.assertEqual(lock.HeldBy(), threading.get_ident())
			self.assertTrue(lock.IsHeldByThisThread())

		# now, the lock should be released
		self.assertFalse(lock.locked())
		self.assertEqual(lock.HeldBy(), None)
		self.assertFalse(lock.IsHeldByThisThread())


		# Now let's try the acquire API
		self.assertTrue(lock.acquire())

		self.assertTrue(lock.locked())
		self.assertEqual(lock.HeldBy(), threading.get_ident())
		self.assertTrue(lock.IsHeldByThisThread())

		with self.assertRaises(SelfLockError):
			lock.acquire()

		# the lock should still be held by the current thread
		self.assertTrue(lock.locked())
		self.assertEqual(lock.HeldBy(), threading.get_ident())
		self.assertTrue(lock.IsHeldByThisThread())

		# release the lock
		lock.release()

		# now, the lock should be released
		self.assertFalse(lock.locked())
		self.assertEqual(lock.HeldBy(), None)
		self.assertFalse(lock.IsHeldByThisThread())

