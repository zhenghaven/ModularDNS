#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import threading


class SelfLockError(Exception):
	'''
	SelfLockError - Self Lock Error

	This exception is raised when a thread holds the lock,
	and when it tries to acquire the lock again.
	'''

	pass


class LockwSLD:
	'''
	LockwSLD - Lock with Self Lock Detection

	The built-in lock in python is not guaranteed that
	when a thread holds the lock,
	and when it tries to acquire the lock again,
	it will throw an exception.

	LockwSLD is a lock with self lock detection.
	So when a thread holds the lock,
	and when it tries to acquire the lock again,
	it will throw an exception.
	'''

	UNDERLYING_LOCK = threading.Lock

	def __init__(self) -> None:
		self.lock = self.UNDERLYING_LOCK()

		self.heldBy = None

	def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
		'''
		acquire - Acquire the lock

		- Parameters:
			- blocking: Whether to block until the lock is acquired
			- timeout: Timeout for blocking
		'''

		selfId = threading.get_ident()
		if self.heldBy == selfId:
			raise SelfLockError('Self lock detected')

		# ok, it's a different thread
		res = self.lock.acquire(blocking=blocking, timeout=timeout)

		if res:
			# at this point, we have acquired the lock
			# set the held-by to the current thread
			self.heldBy = selfId

		return res

	def release(self) -> None:
		'''
		release - Release the lock
		'''

		# Before releasing the lock, reset the held-by.
		# Since the current thread is executing the code here,
		# we don't need to worry about a race condition, where
		# this thread is checking the held-by value.
		self.heldBy = None
		self.lock.release()

	def __enter__(self) -> bool:
		return self.acquire()

	def __exit__(self, exc_type, exc_value, traceback) -> None:
		self.release()

	def locked(self) -> bool:
		'''
		locked - Whether the lock is held by any thread
		'''

		return self.lock.locked()

	def IsHeldByThisThread(self) -> bool:
		'''
		IsHeldByThisThread - Whether the lock is held by the current thread
		'''

		return self.heldBy == threading.get_ident()

	def HeldBy(self) -> int:
		'''
		HeldBy - Get the thread id that holds the lock
		'''

		return self.heldBy

