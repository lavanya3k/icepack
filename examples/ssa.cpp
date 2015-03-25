
#include "ssa.hpp"
#include "rhs.hpp"

using namespace dealii;

int main ()
{
  try
    {
      dealii::deallog.depth_console (0);

      Triangulation<2> tri;
      GridGenerator::hyper_cube(tri, -1, 1);
      RightHandSide<2> rhs;
      Step8::ElasticProblem elastic_problem_2d(tri, rhs);
      elastic_problem_2d.run ();
    }
  catch (std::exception &exc)
    {
      std::cerr << std::endl << std::endl
                << "----------------------------------------------------"
                << std::endl;
      std::cerr << "Exception on processing: " << std::endl
                << exc.what() << std::endl
                << "Aborting!" << std::endl
                << "----------------------------------------------------"
                << std::endl;

      return 1;
    }
  catch (...)
    {
      std::cerr << std::endl << std::endl
                << "----------------------------------------------------"
                << std::endl;
      std::cerr << "Unknown exception!" << std::endl
                << "Aborting!" << std::endl
                << "----------------------------------------------------"
                << std::endl;
      return 1;
    }

  return 0;
}