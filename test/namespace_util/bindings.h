#pragma once

namespace A1 {
	namespace A2 {
		// Leave empty beside of namespace A3 to check that A2 is created
		// correctly without any other content
		namespace A3 {
			static const int in_a3 = 0;
		}
	}
	static const int in_a1 = 1;
}

// namespace B0 is supposed to be flattened into the global namespace
namespace B0 {
	static const int in_global_a = 0;
	namespace B1 {
		static const int in_b1 = 3;

		enum test_enum {
			enum_0 = 0,
			enum_1 = 1
		};
	}
}

static const int in_global_b = 1;
