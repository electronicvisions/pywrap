#pragma once

#include <mutex>

extern "C" {
#include <omp.h>
}

namespace pywrap {

class OMPLock {
public:
  OMPLock() { omp_init_lock(&m_lock); }
  ~OMPLock() { omp_destroy_lock(&m_lock); }

  void lock() { omp_set_lock(&m_lock); }

  void unlock() { omp_unset_lock(&m_lock); }

private:
  omp_lock_t m_lock;
};

typedef std::unique_lock<OMPLock> ScopedOMPGuard;

} // end namespace pywrap
