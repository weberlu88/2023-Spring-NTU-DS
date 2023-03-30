#ifndef RPCS_H
#define RPCS_H

#include "chord.h"
#include "rpc/client.h"

#include <iostream>
#include <cstdint>

Node self, successor, predecessor;
Node finger_table[4];
Node successor_list[3];

Node get_info() { return self; } // Do not modify this line.
Node get_predecessor() { return predecessor; }
Node get_successor() { return successor; }
// Node get_finger_table_0() {return finger_table[0]; }
// Node get_finger_table_3() {return finger_table[3]; }
Node* get_finger_table() { return finger_table; }


void create() {
  predecessor.ip = "";
  successor = self;
}

void change_predecessor(Node n) {
  predecessor = n;
}

void change_successor(Node n) {
  successor = n;
}

void join(Node n) { // n is a known node on Chrod ring
  predecessor.ip = "";
  rpc::client client(n.ip, n.port); // get the known node instance

  successor = client.call("find_successor", self.id).as<Node>(); // use the known node to find the successor by new node id
}

bool isBetween_inclusive(uint64_t id, uint64_t predecessor_id, uint64_t successor_id){
  if (successor_id > predecessor_id) {
    if (id > predecessor_id && id <= successor_id) {
      return true;
    } else {
      return false;
    }
  } else { // successor_id <= predecessor_id
    if ( id > predecessor_id || id <= successor_id) {
      return true;
    } else {
      return false;
    }
  }
}

bool isBetween(uint64_t id, uint64_t predecessor_id, uint64_t successor_id){
  if (successor_id > predecessor_id) {
    if (id > predecessor_id && id < successor_id) {
      return true;
    } else {
      return false;
    }
  } else { // successor_id <= predecessor_id
    if ( id > predecessor_id || id < successor_id) {
      return true;
    } else {
      return false;
    }
  }
}

uint64_t add_id(uint64_t id_1, uint64_t id_2) {
  return (id_1 + id_2) & ((1UL << 32) - 1);
}

Node closest_preceding_node (uint64_t id) {
  for ( int i = 3; i >= 0; i-- ) {
    
    // if (self.id == 373792412 && id == 100663296) {
    //   std::cout << "ID:" << id << "\n";
    //   std::cout << "Finger id:" << finger_table[i].id << "\n";
    //   std::cout << "Self id:" << self.id << "\n";
    // }    

    if ( isBetween(finger_table[i].id, self.id, id) ) {
      if (finger_table[i].id != 0 && finger_table[i].id != self.id){

        return finger_table[i];
      } 
    }

    // if ( finger_table[i].id > self.id && finger_table[i].id < id) {
    //   return finger_table[i];
    // }
  }

  return self;
}

/* finger table version */
Node find_successor(uint64_t id) {
  // TODO: implement your `find_successor` RPC
  Node closest_node;
  try {

    // if ( self.id == successor.id ){ // only one node

    //   return successor;
    if ( isBetween_inclusive(id, self.id, successor.id) ){
      // std::cout << "Node:" << self.id << ": Direct Return \n";

      return successor;

    } else {

      // std::cout << "Node:" << self.id << ": RPC Return\n";
 
      closest_node = closest_preceding_node(id);
      if (closest_node.id == self.id) {
        // if (self.id == 373792412) {
        //   std::cout << "Finger table:" << "\n";
        //   std::cout << "    finger 0:" << finger_table[0].id << "\n";
        //   std::cout << "    finger 1:" << finger_table[1].id << "\n";
        //   std::cout << "    finger 2:" << finger_table[2].id << "\n";
        //   std::cout << "    finger 3:" << finger_table[3].id << "\n";
        // }
        return self;
      } else {
        rpc::client client(closest_node.ip, closest_node.port); 
        return client.call("find_successor", id).as<Node>();
      }


      // rpc::client client(successor.ip, successor.port); 
      // return client.call("find_successor", id).as<Node>();
    }

  } catch (std::exception &e) {
    // Handling Fail
    // std::cout << "Node:" << self.id << ":find_successor err" << "\n" ;
    // std::cout << "     Close Node:" << closest_node.id << "\n" ;

    // successor.ip = "";

  }
  return self;
}

uint64_t next = 0;
void fix_fingers(){
  try {
    if (next >= 4){
      next = 0;
    }

    if (next != 0){
      finger_table[next] = find_successor( add_id(self.id, (1ULL << (28+next)) ) );
    } else {
      finger_table[next] = successor;
    }

    // std::cout << "Node:" << self.id << "\n";
    // std::cout << "        Finger " << next << " ID:" << add_id(self.id, (1ULL << (28+next)) ) << "\n";
    // std::cout << "        Finger " << next << " Node:" << finger_table[next].id << "\n";
    
    next = next + 1;
  } catch (std::exception &e) {
    std::cout << "fix_fingers err" << "\n" ;
  } 
}

void stablize(){

  try {

    Node pre_node;
    // uint64_t temp_su_id = successor.id;
    // std::cout << "Node:" << self.id << "\n";
    // std::cout << "    temp id:" << temp_su_id << "\n";

    // std::cout << "IN sta:" << self.port << ":" << successor.port << "\n";
    if ( successor.id != 0 && self.id != successor.id ) {

      rpc::client client(successor.ip, successor.port); 
      pre_node = client.call("get_predecessor").as<Node>();

    } else { // when only have root node [self.id == successor.id]
      pre_node = predecessor;
      // std::cout << "IN sta:" << pre_node.id << "\n";
    }

    if (pre_node.id != 0) { // check if pre_node exist. if exist, check weather to change the successor

      if ( isBetween(pre_node.id, self.id, successor.id) ) {
        successor = pre_node;
        // std::cout << "    change id:" << successor.id << "\n";
      } 
    } 
    
    if ( successor.id != 0 && self.id != successor.id) {
      // if (temp_su_id != successor.id) { // if successor change, tell it to change predecessor
      rpc::client client2(successor.ip, successor.port);
      // std::cout << "Notify Node  :" << successor.port << "\n";
      client2.call("notify", self);   
      // }
    }

  } catch (std::exception &e) {
    // std::cout << &e. << "\n" ;
    std::cout << "stablize Err \n";

  }

}

void notify(Node n){
  // std::cout << "In notify  :" << self.port << "\n";
  // std::cout << "In notify  :" << predecessor.ip << "\n";

  if ( predecessor.ip == "" || isBetween(n.id, predecessor.id, self.id) ) {
    predecessor = n;
    // std::cout << "notify()" << "\n" ;
  }

  // if ( predecessor.ip == "" || (n.id > predecessor.id && n.id < self.id)  ) {
  //   predecessor = n;
  //   // std::cout << "notify()" << "\n" ;
  // }
}

void check_predecessor() {
  try {
    rpc::client client(predecessor.ip, predecessor.port);
    Node n = client.call("get_info").as<Node>();
  } catch (std::exception &e) {
    predecessor.ip = "";
    // std::cout << "check_predecessor Err \n";
  }
}

void register_rpcs() {
  add_rpc("get_info", &get_info); // Do not modify this line.

  add_rpc("get_predecessor", &get_predecessor); 
  add_rpc("change_predecessor", &change_predecessor);
  add_rpc("get_successor", &get_successor);
  add_rpc("change_successor", &change_successor);
  add_rpc("notify", &notify);
  // add_rpc("get_finger_table_0", &get_finger_table_0);
  // add_rpc("get_finger_table", &get_finger_table);

  add_rpc("create", &create);
  add_rpc("join", &join);
  add_rpc("find_successor", &find_successor);
}

void register_periodics() {
  add_periodic(check_predecessor);
  add_periodic(stablize);
  add_periodic(fix_fingers);
}

#endif /* RPCS_H */
