#pragma once

#include <mutex>

extern "C" {
#include <omp.h>
}

namespace pywrap {

class OMPLock {
public:
	OMPLock() : m_locked(false) { omp_init_nest_lock(&m_lock); }
	~OMPLock()
	{
		if (m_locked)
			unlock();
		omp_destroy_nest_lock(&m_lock);
	}

	void lock()
	{
		omp_set_nest_lock(&m_lock);
		m_locked = true;
	}

	void unlock()
	{
		m_locked = false;
		omp_unset_nest_lock(&m_lock);
	}

private:
	omp_nest_lock_t m_lock;
	bool m_locked;
};

typedef std::unique_lock<OMPLock> ScopedOMPGuard;

} // pywrap
