#include <vector>
#include <string>

inline std::vector<std::string> get_string_vector()
{
	std::vector<std::string> ret;
	ret.push_back("Hello");
	ret.push_back("World!!!");
	return ret;
}


namespace test
{
	typedef std::vector<std::string> String1;
	typedef String1 String2;
	typedef String2 String3;
	typedef String2 String4;
	typedef const std::vector<std::string> & StringVectorConstRef;
	typedef std::vector<std::string> &       StringVectorRef;
	typedef std::vector<std::string> *       StringVectorPtr;
}

